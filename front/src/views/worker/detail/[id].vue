<script setup lang="ts">
import { showToast, showImagePreview } from 'vant'
import apiWorker from '@/api/modules/worker'

definePage({
  name: 'worker-detail',
  meta: {
    title: '家政阿姨详情',
  },
})

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const worker = ref<any>(null)
const workerId = computed(() => {
  const params = route.params as any
  return params.id as string
})

// 判断是否显示预约按钮（只有普通用户才显示）
const showBookButton = computed(() => {
  return userStore.userInfo?.role === 'user' && worker.value?.is_available
})

// 获取详情
async function getWorkerDetail() {
  loading.value = true
  try {
    const res: any = await apiWorker.getWorkerDetail(workerId.value)
    if (res.code === 200) {
      worker.value = res.data
    }
  }
  catch (error: any) {
    showToast(error.message || '加载失败')
  }
  finally {
    loading.value = false
  }
}

// 联系客服
function contactService() {
  showToast('客服功能开发中')
}

// 立即预约
function bookNow() {
  if (!userStore.isLogin) {
    showToast('请先登录')
    router.push('/login')
    return
  }
  router.push(`/order/book?workerId=${workerId.value}`)
}

// 预览图片
function previewImage(url: string) {
  if (!url)
    return
  
  // 收集所有证书图片
  const images: string[] = []
  if (worker.value.id_card_front)
    images.push(worker.value.id_card_front)
  if (worker.value.id_card_back)
    images.push(worker.value.id_card_back)
  if (worker.value.health_certificate)
    images.push(worker.value.health_certificate)
  if (worker.value.health_report)
    images.push(worker.value.health_report)
  if (worker.value.practice_certificate)
    images.push(worker.value.practice_certificate)
  
  // 使用 Vant 的 ImagePreview
  showImagePreview({
    images,
    startPosition: images.indexOf(url),
  })
}

onMounted(() => {
  getWorkerDetail()
})
</script>

<template>
  <div class="worker-detail-page" :class="{ 'has-footer': showBookButton }">
    <van-nav-bar
      title="阿姨详情"
      left-arrow
      @click-left="router.back()"
      class="nav-bar"
    />

    <van-loading v-if="loading" class="loading" />

    <div v-else-if="worker" class="content">
      <!-- 头部区域 - 玻璃拟态风格 -->
      <div class="profile-header">
        <!-- 背景模糊层 -->
        <div class="header-bg" />
        
        <!-- 人物信息卡片 -->
        <div class="profile-card">
          <div class="card-main">
            <!-- 头像 -->
            <div class="avatar-wrapper">
              <img
                v-if="worker.id_card_front"
                :src="worker.id_card_front"
                alt="头像"
                class="avatar"
              >
              <div v-else class="avatar avatar-placeholder">
                {{ worker.real_name.charAt(0) }}
              </div>
              <van-tag
                v-if="worker.is_available"
                plain
                color="#07C160"
                class="status-tag"
              >
                可接单
              </van-tag>
              <van-tag
                v-else
                plain
                color="#999"
                class="status-tag"
              >
                休息中
              </van-tag>
            </div>

            <!-- 基本信息 -->
            <div class="profile-info">
              <div class="name-row">
                <span class="name">{{ worker.real_name }}</span>
                <span class="age">{{ worker.age }}岁</span>
                <van-tag
                  v-if="worker.is_recommended"
                  color="#FF9F43"
                  class="recommend-tag"
                >
                  <van-icon name="fire-o" size="10" />
                  推荐
                </van-tag>
              </div>
              <div class="meta-row">
                <span class="meta-item">
                  <van-icon name="friends-o" size="14" />
                  {{ worker.gender === 'female' ? '女' : '男' }}
                </span>
                <span class="meta-divider">|</span>
                <span class="meta-item">
                  <van-icon name="bag-o" size="14" />
                  {{ worker.experience_years }}年经验
                </span>
              </div>
              <div class="rating-row">
                <van-rate
                  :model-value="worker.rating"
                  :size="14"
                  color="#FF9F43"
                  void-color="#E5E5E5"
                  readonly
                />
                <span class="rating-text">{{ worker.rating }}</span>
                <span class="order-text">已服务{{ worker.completed_orders }}单</span>
              </div>
            </div>
          </div>

          <!-- 价格标签 -->
          <div class="price-tag">
            <span class="price-value">¥{{ worker.hourly_rate || '--' }}</span>
            <span class="price-unit">/小时</span>
          </div>
        </div>
      </div>

      <!-- 数据仪表盘 -->
      <div class="stats-dashboard">
        <van-grid :border="false" :column-num="4">
          <van-grid-item>
            <div class="stat-item">
              <div class="stat-value">{{ worker.rating || 5.0 }}</div>
              <div class="stat-label">评分</div>
            </div>
          </van-grid-item>
          <van-grid-item>
            <div class="stat-item">
              <div class="stat-value">{{ worker.completed_orders || 0 }}</div>
              <div class="stat-label">订单</div>
            </div>
          </van-grid-item>
          <van-grid-item>
            <div class="stat-item">
              <div class="stat-value">{{ worker.experience_years || 0 }}</div>
              <div class="stat-label">经验</div>
            </div>
          </van-grid-item>
          <van-grid-item>
            <div class="stat-item">
              <div class="stat-value" :class="{ 'available': worker.is_available }">
                {{ worker.is_available ? '在线' : '休息' }}
              </div>
              <div class="stat-label">状态</div>
            </div>
          </van-grid-item>
        </van-grid>
      </div>

      <!-- 擅长技能 -->
      <div v-if="worker.skills && worker.skills.length > 0" class="section">
        <div class="section-title">擅长技能</div>
        <div class="skills-list">
          <van-tag
            v-for="skill in worker.skills"
            :key="skill"
            plain
            color="#FF9F43"
            size="large"
          >
            {{ skill }}
          </van-tag>
        </div>
      </div>

      <!-- 个人简介 -->
      <div v-if="worker.introduction" class="section">
        <div class="section-title">个人简介</div>
        <div class="bio-content">
          {{ worker.introduction }}
        </div>
      </div>

      <!-- 联系方式 -->
      <div class="section">
        <div class="section-title">联系方式</div>
        <van-cell-group inset>
          <van-cell title="联系电话" :value="worker.phone" icon="phone-o" />
          <van-cell title="居住地址" :value="worker.address" icon="location-o" />
        </van-cell-group>
      </div>

      <!-- 服务区域 -->
      <div v-if="worker.service_areas && worker.service_areas.length > 0" class="section">
        <div class="section-title">服务区域</div>
        <div class="service-areas">
          <van-tag
            v-for="area in worker.service_areas"
            :key="area"
            plain
            color="#FF9F43"
          >
            {{ area }}
          </van-tag>
        </div>
      </div>

      <!-- 资质证书 -->
      <div class="section">
        <div class="section-title">资质证书</div>
        <div class="certificates-gallery">
          <div
            v-if="worker.id_card_front"
            class="cert-card"
            @click="previewImage(worker.id_card_front)"
          >
            <van-image
              :src="worker.id_card_front"
              fit="cover"
              class="cert-image"
            />
            <div class="cert-overlay">
              <span class="cert-name">身份证人像面</span>
            </div>
          </div>
          <div
            v-if="worker.id_card_back"
            class="cert-card"
            @click="previewImage(worker.id_card_back)"
          >
            <van-image
              :src="worker.id_card_back"
              fit="cover"
              class="cert-image"
            />
            <div class="cert-overlay">
              <span class="cert-name">身份证国徽面</span>
            </div>
          </div>
          <div
            v-if="worker.health_certificate"
            class="cert-card"
            @click="previewImage(worker.health_certificate)"
          >
            <van-image
              :src="worker.health_certificate"
              fit="cover"
              class="cert-image"
            />
            <div class="cert-overlay">
              <span class="cert-name">健康证</span>
            </div>
          </div>
          <div
            v-if="worker.health_report"
            class="cert-card"
            @click="previewImage(worker.health_report)"
          >
            <van-image
              :src="worker.health_report"
              fit="cover"
              class="cert-image"
            />
            <div class="cert-overlay">
              <span class="cert-name">体检报告</span>
            </div>
          </div>
          <div
            v-if="worker.practice_certificate"
            class="cert-card"
            @click="previewImage(worker.practice_certificate)"
          >
            <van-image
              :src="worker.practice_certificate"
              fit="cover"
              class="cert-image"
            />
            <div class="cert-overlay">
              <span class="cert-name">执业证书</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div v-if="showBookButton" class="footer-bar">
      <van-button
        icon="service-o"
        plain
        class="contact-btn"
        @click="contactService"
      >
        联系客服
      </van-button>
      <van-button
        type="primary"
        class="book-btn"
        @click="bookNow"
      >
        立即预约
      </van-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.worker-detail-page {
  min-height: 100vh;
  background: #F7F8FA;
  padding-bottom: 20px;

  &.has-footer {
    padding-bottom: 80px;
  }
}

.nav-bar {
  :deep(.van-nav-bar__title) {
    font-weight: 600;
  }
}

.loading {
  padding: 100px 0;
}

.content {
  padding-bottom: 12px;
}

// 头部区域 - 玻璃拟态
.profile-header {
  position: relative;
  padding: 20px 16px 24px;
  margin-bottom: 12px;

  .header-bg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 180px;
    background: linear-gradient(135deg, #FF9F43 0%, #FFAD60 100%);
    filter: blur(40px);
    opacity: 0.3;
    z-index: 0;
  }

  .profile-card {
    position: relative;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(255, 159, 67, 0.15);
    z-index: 1;

    .card-main {
      display: flex;
      gap: 16px;
      margin-bottom: 16px;

      .avatar-wrapper {
        position: relative;
        flex-shrink: 0;

        .avatar {
          width: 80px;
          height: 80px;
          border-radius: 12px;
          object-fit: cover;
          border: 3px solid #FFF;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

          &.avatar-placeholder {
            background: linear-gradient(135deg, #FF9F43 0%, #FF7F50 100%);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            font-weight: bold;
          }
        }

        .status-tag {
          position: absolute;
          bottom: -6px;
          left: 50%;
          transform: translateX(-50%);
          font-size: 11px;
          padding: 2px 8px;
          border-radius: 10px;
          white-space: nowrap;
        }
      }

      .profile-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 8px;

        .name-row {
          display: flex;
          align-items: center;
          gap: 8px;

          .name {
            font-size: 22px;
            font-weight: bold;
            color: #333;
          }

          .age {
            font-size: 15px;
            color: #999;
          }

          .recommend-tag {
            font-size: 11px;
            padding: 2px 6px;
            height: 18px;
            line-height: 14px;
          }
        }

        .meta-row {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: #666;

          .meta-item {
            display: flex;
            align-items: center;
            gap: 4px;
          }

          .meta-divider {
            color: #DCDEE0;
          }
        }

        .rating-row {
          display: flex;
          align-items: center;
          gap: 6px;

          .rating-text {
            font-size: 14px;
            font-weight: 600;
            color: #FF9F43;
            margin-left: 2px;
          }

          .order-text {
            font-size: 12px;
            color: #999;
            margin-left: 4px;
          }
        }
      }
    }

    .price-tag {
      display: flex;
      align-items: baseline;
      justify-content: center;
      padding: 12px;
      background: linear-gradient(135deg, #FFF5E6 0%, #FFE8CC 100%);
      border-radius: 12px;

      .price-value {
        font-size: 28px;
        font-weight: bold;
        color: #FF9F43;
      }

      .price-unit {
        font-size: 14px;
        color: #FF9F43;
        margin-left: 4px;
      }
    }
  }
}

// 数据仪表盘
.stats-dashboard {
  background: #fff;
  border-radius: 12px;
  margin: 0 12px 12px;
  overflow: hidden;

  :deep(.van-grid-item__content) {
    padding: 16px 8px;
  }

  .stat-item {
    text-align: center;

    .stat-value {
      font-size: 20px;
      font-weight: bold;
      color: #333;
      margin-bottom: 4px;

      &.available {
        color: #07C160;
      }
    }

    .stat-label {
      font-size: 12px;
      color: #999;
    }
  }
}

// 内容区块
.section {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin: 0 12px 12px;

  .section-title {
    font-size: 16px;
    font-weight: bold;
    color: #333;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #F5F7FA;
  }

  .skills-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    :deep(.van-tag) {
      font-size: 14px;
      padding: 6px 12px;
    }
  }

  .bio-content {
    padding: 12px;
    background: #F7F8FA;
    border-radius: 8px;
    font-size: 14px;
    color: #666;
    line-height: 1.8;
  }

  .service-areas {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  :deep(.van-cell-group) {
    margin: 0 -16px;
    border-radius: 0;

    .van-cell {
      padding: 12px 16px;

      &::after {
        border-color: #F5F7FA;
      }
    }
  }
}

// 证书画廊
.certificates-gallery {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;

  .cert-card {
    position: relative;
    aspect-ratio: 4/3;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s;

    &:active {
      transform: scale(0.98);
    }

    .cert-image {
      width: 100%;
      height: 100%;

      :deep(img) {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }

    .cert-overlay {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 8px 12px;
      background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
      display: flex;
      align-items: center;
      justify-content: center;

      .cert-name {
        font-size: 13px;
        color: #fff;
        font-weight: 500;
      }
    }
  }
}

// 底部操作栏
.footer-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px;
  padding-bottom: calc(12px + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
  z-index: 100;
  display: flex;
  gap: 12px;

  .contact-btn {
    flex: 1;
    height: 44px;
    border-color: #FF9F43;
    color: #FF9F43;
    font-size: 14px;

    &:active {
      background: #FFF5E6;
    }
  }

  .book-btn {
    flex: 2;
    height: 44px;
    background: linear-gradient(135deg, #FF9F43 0%, #FF7F50 100%);
    border: none;
    font-size: 16px;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(255, 159, 67, 0.3);

    &:active {
      opacity: 0.9;
    }
  }
}
</style>
