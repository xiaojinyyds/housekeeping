<script setup lang="ts">
import { showToast, showConfirmDialog } from 'vant'
import apiAdmin from '@/api/modules/admin'

definePage({
  name: 'admin-workers',
  meta: {
    title: '阿姨管理',
    auth: true,
  },
})

const router = useRouter()
const userStore = useUserStore()

// 检查权限
if (!userStore.isAdmin) {
  showToast('无权访问')
  router.replace('/')
}

const loading = ref(false)
const finished = ref(false)
const workerList = ref<any[]>([])
const page = ref(1)
const pageSize = 10

// 筛选条件
const activeTab = ref('all')
const tabs = [
  { name: 'all', title: '全部' },
  { name: 'available', title: '接单中' },
  { name: 'unavailable', title: '休息中' },
]

// 搜索关键词
const searchKeyword = ref('')

// 获取阿姨列表
async function getWorkers(isRefresh = false) {
  if (isRefresh) {
    page.value = 1
    workerList.value = []
    finished.value = false
  }

  loading.value = true
  try {
    const params: any = {
      page: page.value,
      page_size: pageSize,
    }

    if (activeTab.value === 'available') {
      params.is_available = true
    }
    else if (activeTab.value === 'unavailable') {
      params.is_available = false
    }

    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }

    const res: any = await apiAdmin.getWorkers(params)

    if (res.code === 200) {
      if (isRefresh) {
        workerList.value = res.data.list
      }
      else {
        workerList.value.push(...res.data.list)
      }

      if (res.data.list.length < pageSize) {
        finished.value = true
      }
      else {
        page.value++
      }
    }
  }
  catch (error: any) {
    showToast(error.message || '加载失败')
    finished.value = true
  }
  finally {
    loading.value = false
  }
}

// 切换标签
function onTabChange() {
  getWorkers(true)
}

// 搜索
function onSearch() {
  getWorkers(true)
}

// 下拉刷新
async function onRefresh() {
  await getWorkers(true)
}

// 上拉加载
async function onLoad() {
  await getWorkers()
}

// 切换接单状态
async function toggleWorkerStatus(worker: any) {
  const newStatus = !worker.is_available
  const action = newStatus ? '上架' : '下架'

  try {
    await showConfirmDialog({
      title: `确认${action}`,
      message: `确定要${action}阿姨 ${worker.real_name} 吗？`,
    })

    const res: any = await apiAdmin.updateWorkerAvailable(worker.id, newStatus)

    if (res.code === 200) {
      showToast(`${action}成功`)
      worker.is_available = newStatus
    }
  }
  catch (error: any) {
    if (error !== 'cancel') {
      showToast(error.message || '操作失败')
    }
  }
}

// 切换推荐状态
async function toggleRecommendStatus(worker: any) {
  const newStatus = !worker.is_recommended
  const action = newStatus ? '设为首页推荐' : '取消首页推荐'

  try {
    await showConfirmDialog({
      title: `确认${action}`,
      message: `确定要${action}阿姨 ${worker.real_name} 吗？`,
    })

    const res: any = await apiAdmin.updateWorkerRecommend(worker.id, newStatus)

    if (res.code === 200) {
      showToast(`${action}成功`)
      worker.is_recommended = newStatus
    }
  }
  catch (error: any) {
    if (error !== 'cancel') {
      showToast(error.message || '操作失败')
    }
  }
}

// 查看详情
function viewDetail(worker: any) {
  router.push(`/worker/detail/${worker.user_id}`)
}

onMounted(() => {
  getWorkers(true)
})
</script>

<template>
  <div class="admin-workers-page">
    <van-nav-bar
      title="阿姨管理"
      left-arrow
      @click-left="router.back()"
      class="nav-bar"
    >
      <template #right>
        <van-icon name="plus" size="20" @click="router.push('/admin/create-worker')" />
      </template>
    </van-nav-bar>

    <!-- 搜索栏 -->
    <div class="search-section">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索姓名/手机号"
        @search="onSearch"
        @clear="onSearch"
      />
    </div>

    <!-- 标签页 -->
    <van-tabs v-model:active="activeTab" @change="onTabChange" sticky>
      <van-tab
        v-for="tab in tabs"
        :key="tab.name"
        :name="tab.name"
        :title="tab.title"
      >
        <van-pull-refresh v-model="loading" @refresh="onRefresh">
          <van-list
            v-model:loading="loading"
            :finished="finished"
            finished-text="没有更多了"
            @load="onLoad"
          >
            <div class="worker-list">
              <div
                v-for="worker in workerList"
                :key="worker.id"
                class="worker-card"
              >
                <!-- 卡片头部 -->
                <div class="card-header">
                  <!-- 左侧头像 -->
                  <div class="avatar-wrapper">
                    <div class="avatar">
                      {{ worker.real_name.charAt(0) }}
                    </div>
                    <van-tag
                      v-if="worker.is_available"
                      color="#07C160"
                      class="status-badge"
                    >
                      接单中
                    </van-tag>
                    <van-tag
                      v-else
                      color="#999"
                      class="status-badge"
                    >
                      休息中
                    </van-tag>
                  </div>

                  <!-- 中间信息 -->
                  <div class="worker-info">
                    <div class="worker-name">
                      {{ worker.real_name }}
                      <span class="worker-age">{{ worker.age }}岁</span>
                      <van-tag
                        v-if="worker.is_recommended"
                        color="#FF9F43"
                        class="recommend-badge"
                      >
                        <van-icon name="fire-o" size="10" />
                        推荐
                      </van-tag>
                    </div>
                    <div class="worker-meta">
                      <van-rate
                        :model-value="worker.rating"
                        size="12"
                        color="#FF9F43"
                        void-color="#eee"
                        readonly
                      />
                      <span class="rating-text">{{ worker.rating }}</span>
                      <span class="divider">|</span>
                      <span class="order-count">{{ worker.completed_orders }}单</span>
                    </div>
                  </div>

                  <!-- 右侧开关 -->
                  <van-switch
                    :model-value="worker.is_available"
                    size="20"
                    @update:model-value="toggleWorkerStatus(worker)"
                  />
                </div>

                <!-- 卡片内容 -->
                <div class="card-body">
                  <div class="info-item">
                    <van-icon name="phone-o" size="14" color="#999" />
                    <span class="info-text">{{ worker.phone }}</span>
                  </div>
                  <div class="info-item">
                    <van-icon name="location-o" size="14" color="#999" />
                    <span class="info-text">{{ worker.address }}</span>
                  </div>
                  <div class="info-item">
                    <van-icon name="bag-o" size="14" color="#999" />
                    <span class="info-text">{{ worker.experience_years }}年经验</span>
                  </div>
                  <div class="info-item skills">
                    <van-icon name="star-o" size="14" color="#999" />
                    <div class="skills-tags">
                      <van-tag
                        v-for="skill in worker.skills"
                        :key="skill"
                        plain
                        color="#FF9F43"
                      >
                        {{ skill }}
                      </van-tag>
                    </div>
                  </div>
                  <div v-if="worker.hourly_rate" class="info-item">
                    <van-icon name="gold-coin-o" size="14" color="#999" />
                    <span class="info-text price">¥{{ worker.hourly_rate }}/小时</span>
                  </div>
                </div>

                <!-- 卡片底部 -->
                <div class="card-footer">
                  <van-button
                    size="small"
                    round
                    plain
                    @click="viewDetail(worker)"
                  >
                    查看详情
                  </van-button>
                  <van-button
                    size="small"
                    round
                    :type="worker.is_recommended ? 'warning' : 'default'"
                    plain
                    @click="toggleRecommendStatus(worker)"
                  >
                    <van-icon :name="worker.is_recommended ? 'star' : 'star-o'" size="12" />
                    {{ worker.is_recommended ? '已推荐' : '推荐' }}
                  </van-button>
                </div>
              </div>
            </div>
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>
  </div>
</template>

<style scoped lang="scss">
.admin-workers-page {
  min-height: 100vh;
  background: #F7F8FA;
}

.nav-bar {
  background: linear-gradient(135deg, #FF9F43 0%, #FF7F50 100%);

  :deep(.van-nav-bar__title) {
    color: #fff;
  }

  :deep(.van-icon) {
    color: #fff;
  }
}

// 搜索区域
.search-section {
  background: #fff;
  padding: 8px 0;

  :deep(.van-search) {
    padding: 8px 16px;
  }
}

// 阿姨列表
.worker-list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;

  .worker-card {
    background: #fff;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

    // 卡片头部
    .card-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;

      .avatar-wrapper {
        flex-shrink: 0;
        position: relative;

        .avatar {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: linear-gradient(135deg, #FF9F43 0%, #FF7F50 100%);
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          font-weight: bold;
        }

        .status-badge {
          position: absolute;
          bottom: -4px;
          left: 50%;
          transform: translateX(-50%);
          font-size: 10px;
          padding: 0 4px;
          height: 16px;
          line-height: 16px;
          border-radius: 8px;
        }
      }

      .worker-info {
        flex: 1;
        min-width: 0;

        .worker-name {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 16px;
          font-weight: bold;
          color: #333;
          margin-bottom: 6px;

          .worker-age {
            font-size: 13px;
            font-weight: normal;
            color: #999;
          }

          .recommend-badge {
            font-size: 11px;
            padding: 2px 6px;
            height: 18px;
            line-height: 14px;
          }
        }

        .worker-meta {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: #999;

          .rating-text {
            color: #FF9F43;
            font-weight: 500;
          }

          .divider {
            color: #DCDEE0;
          }

          .order-count {
            color: #666;
          }
        }
      }
    }

    // 卡片内容
    .card-body {
      margin-bottom: 12px;

      .info-item {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        margin-bottom: 8px;
        font-size: 13px;

        &:last-child {
          margin-bottom: 0;
        }

        .info-text {
          flex: 1;
          color: #666;
          line-height: 1.5;

          &.price {
            color: #FF9F43;
            font-weight: 500;
          }
        }

        &.skills {
          .skills-tags {
            flex: 1;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
          }
        }
      }
    }

    // 卡片底部
    .card-footer {
      display: flex;
      gap: 8px;
      padding-top: 12px;
      border-top: 1px solid #F5F7FA;

      :deep(.van-button) {
        flex: 1;
        height: 32px;
        padding: 0 12px;
        font-size: 13px;
      }
    }
  }
}

:deep(.van-tabs) {
  .van-tabs__nav {
    background: #fff;
  }

  .van-tab {
    color: #666;
    font-size: 15px;

    &--active {
      color: #FF9F43;
      font-weight: bold;
    }
  }

  .van-tabs__line {
    background: #FF9F43;
  }
}
</style>
