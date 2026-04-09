<script setup lang="ts">
import { showToast, showImagePreview, showDialog } from 'vant'
import apiWorker from '@/api/modules/worker'

definePage({
  name: 'admin-application-detail',
  meta: {
    title: '申请详情',
    auth: true,
  },
})

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 检查权限
if (!userStore.isAdmin) {
  showToast('无权访问')
  router.replace('/')
}

const loading = ref(false)
const application = ref<any>(null)
const showRejectDialog = ref(false)
const rejectReason = ref('')

const applicationId = route.params.id as string

// 获取申请详情
async function getApplicationDetail() {
  loading.value = true
  try {
    // 这里需要后端提供单个申请详情接口，暂时用列表接口模拟
    const res = await apiWorker.getApplications({
      page: 1,
      page_size: 100,
    })

    if (res.code === 200) {
      application.value = res.data.list.find((item: any) => item.id === applicationId)
      if (!application.value) {
        showToast('申请不存在')
        router.back()
      }
    }
  }
  catch (error: any) {
    showToast(error.message || '加载失败')
  }
  finally {
    loading.value = false
  }
}

// 身份证脱敏
function maskIdCard(idCard: string) {
  if (!idCard || idCard.length < 18)
    return idCard
  return `${idCard.substring(0, 6)}********${idCard.substring(14)}`
}

// 预览图片
function previewImage(url: string) {
  showImagePreview({
    images: [url],
    closeable: true,
  })
}

// 预览所有证件
function previewAllCerts() {
  const images = [
    application.value.id_card_front,
    application.value.id_card_back,
    application.value.health_certificate,
    application.value.health_report,
    application.value.practice_certificate,
    ...(application.value.other_certificates || []),
  ].filter(Boolean)

  showImagePreview({
    images,
    closeable: true,
  })
}

// 通过申请
async function approveApplication() {
  try {
    await showDialog({
      title: '确认通过',
      message: `确定通过 ${application.value.real_name} 的申请吗？通过后将自动创建阿姨档案。`,
    })

    const res = await apiWorker.reviewApplication(application.value.id, {
      status: 'approved',
    })

    if (res.code === 200) {
      showToast('审核通过')
      router.back()
    }
  }
  catch (error: any) {
    if (error !== 'cancel') {
      showToast(error.message || '操作失败')
    }
  }
}

// 拒绝申请
function rejectApplication() {
  showRejectDialog.value = true
}

// 确认拒绝
async function confirmReject() {
  if (!rejectReason.value.trim()) {
    showToast('请输入拒绝原因')
    return
  }

  try {
    const res = await apiWorker.reviewApplication(application.value.id, {
      status: 'rejected',
      reject_reason: rejectReason.value,
    })

    if (res.code === 200) {
      showToast('已拒绝')
      showRejectDialog.value = false
      rejectReason.value = ''
      router.back()
    }
  }
  catch (error: any) {
    showToast(error.message || '操作失败')
  }
}

onMounted(() => {
  getApplicationDetail()
})
</script>

<template>
  <div class="application-detail-page">
    <van-nav-bar
      title="申请详情"
      left-arrow
      @click-left="router.back()"
      class="nav-bar"
    />

    <van-loading v-if="loading" class="loading" vertical>
      加载中...
    </van-loading>

    <div v-else-if="application" class="content">
      <!-- 状态卡片 -->
      <div class="status-card" :class="application.status">
        <van-icon
          v-if="application.status === 'pending'"
          name="clock-o"
          size="48"
          color="#FF9F43"
        />
        <van-icon
          v-else-if="application.status === 'approved'"
          name="checked"
          size="48"
          color="#07C160"
        />
        <van-icon
          v-else
          name="close"
          size="48"
          color="#EE0A24"
        />
        <div class="status-text">
          {{ application.status === 'pending' ? '待审核' : application.status === 'approved' ? '已通过' : '已拒绝' }}
        </div>
        <div v-if="application.status === 'rejected' && application.reject_reason" class="reject-reason">
          拒绝原因：{{ application.reject_reason }}
        </div>
      </div>

      <!-- 基本信息 -->
      <div class="info-section">
        <div class="section-title">
          <van-icon name="user-o" size="18" color="#FF9F43" />
          <span>基本信息</span>
        </div>
        <van-cell-group inset>
          <van-cell title="真实姓名" :value="application.real_name" />
          <van-cell title="身份证号" :value="maskIdCard(application.id_card)" />
          <van-cell title="年龄" :value="`${application.age}岁`" />
          <van-cell title="性别" :value="application.gender === 'female' ? '女' : '男'" />
          <van-cell title="联系电话" :value="application.phone" />
          <van-cell title="居住地址" :value="application.address" />
        </van-cell-group>
      </div>

      <!-- 工作信息 -->
      <div class="info-section">
        <div class="section-title">
          <van-icon name="bag-o" size="18" color="#FF9F43" />
          <span>工作信息</span>
        </div>
        <van-cell-group inset>
          <van-cell title="工作年限" :value="`${application.experience_years}年`" />
          <van-cell title="擅长技能">
            <template #value>
              <div class="skills-tags">
                <van-tag
                  v-for="skill in application.skills"
                  :key="skill"
                  plain
                  color="#FF9F43"
                  size="medium"
                >
                  {{ skill }}
                </van-tag>
              </div>
            </template>
          </van-cell>
        </van-cell-group>
      </div>

      <!-- 个人简介 -->
      <div class="info-section">
        <div class="section-title">
          <van-icon name="description" size="18" color="#FF9F43" />
          <span>个人简介</span>
        </div>
        <van-cell-group inset>
          <van-cell>
            <div class="introduction">
              {{ application.introduction }}
            </div>
          </van-cell>
        </van-cell-group>
      </div>

      <!-- 证件照片 -->
      <div class="info-section">
        <div class="section-title">
          <van-icon name="certificate" size="18" color="#FF9F43" />
          <span>证件照片</span>
          <span class="view-all" @click="previewAllCerts">查看全部</span>
        </div>
        <div class="cert-grid">
          <div class="cert-item" @click="previewImage(application.id_card_front)">
            <van-image
              :src="application.id_card_front"
              fit="cover"
              class="cert-image"
            >
              <template #loading>
                <van-loading type="spinner" size="20" />
              </template>
            </van-image>
            <div class="cert-label">身份证人像面</div>
          </div>

          <div class="cert-item" @click="previewImage(application.id_card_back)">
            <van-image
              :src="application.id_card_back"
              fit="cover"
              class="cert-image"
            >
              <template #loading>
                <van-loading type="spinner" size="20" />
              </template>
            </van-image>
            <div class="cert-label">身份证国徽面</div>
          </div>

          <div class="cert-item" @click="previewImage(application.health_certificate)">
            <van-image
              :src="application.health_certificate"
              fit="cover"
              class="cert-image"
            >
              <template #loading>
                <van-loading type="spinner" size="20" />
              </template>
            </van-image>
            <div class="cert-label">健康证</div>
          </div>

          <div class="cert-item" @click="previewImage(application.health_report)">
            <van-image
              :src="application.health_report"
              fit="cover"
              class="cert-image"
            >
              <template #loading>
                <van-loading type="spinner" size="20" />
              </template>
            </van-image>
            <div class="cert-label">体检报告</div>
          </div>

          <div class="cert-item" @click="previewImage(application.practice_certificate)">
            <van-image
              :src="application.practice_certificate"
              fit="cover"
              class="cert-image"
            >
              <template #loading>
                <van-loading type="spinner" size="20" />
              </template>
            </van-image>
            <div class="cert-label">执业证书</div>
          </div>

          <div
            v-for="(cert, index) in application.other_certificates"
            :key="index"
            class="cert-item"
            @click="previewImage(cert)"
          >
            <van-image
              :src="cert"
              fit="cover"
              class="cert-image"
            >
              <template #loading>
                <van-loading type="spinner" size="20" />
              </template>
            </van-image>
            <div class="cert-label">其他证书{{ index + 1 }}</div>
          </div>
        </div>
      </div>

      <!-- 申请时间 -->
      <div class="info-section">
        <van-cell-group inset>
          <van-cell title="申请时间" :value="new Date(application.created_at).toLocaleString()" />
          <van-cell
            v-if="application.reviewed_at"
            title="审核时间"
            :value="new Date(application.reviewed_at).toLocaleString()"
          />
        </van-cell-group>
      </div>

      <!-- 底部操作按钮 -->
      <div v-if="application.status === 'pending'" class="action-section">
        <van-button
          block
          round
          type="danger"
          @click="rejectApplication"
          class="action-btn reject-btn"
        >
          拒绝申请
        </van-button>
        <van-button
          block
          round
          type="success"
          @click="approveApplication"
          class="action-btn approve-btn"
        >
          通过审核
        </van-button>
      </div>
    </div>

    <!-- 拒绝原因对话框 -->
    <van-dialog
      v-model:show="showRejectDialog"
      title="拒绝申请"
      show-cancel-button
      @confirm="confirmReject"
      @cancel="rejectReason = ''"
    >
      <div class="reject-dialog-content">
        <van-field
          v-model="rejectReason"
          type="textarea"
          rows="4"
          placeholder="请输入拒绝原因（必填）"
          maxlength="200"
          show-word-limit
        />
      </div>
    </van-dialog>
  </div>
</template>

<style scoped lang="scss">
.application-detail-page {
  min-height: 100vh;
  background: #F7F8FA;
  padding-bottom: 80px;
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

.loading {
  padding: 100px 0;
  text-align: center;
}

.content {
  padding: 16px;
}

// 状态卡片
.status-card {
  background: #fff;
  border-radius: 16px;
  padding: 32px 20px;
  text-align: center;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

  .status-text {
    font-size: 20px;
    font-weight: bold;
    color: #333;
    margin-top: 12px;
  }

  .reject-reason {
    margin-top: 16px;
    padding: 12px;
    background: #FFF7E6;
    border-radius: 8px;
    font-size: 13px;
    color: #FF9F43;
    text-align: left;
  }
}

// 信息区域
.info-section {
  margin-bottom: 16px;

  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px 8px;
    font-size: 15px;
    font-weight: bold;
    color: #333;

    > span {
      flex: 1;
    }

    .view-all {
      font-size: 13px;
      font-weight: normal;
      color: #FF9F43;
      cursor: pointer;
      margin-left: auto;

      &:active {
        opacity: 0.7;
      }
    }
  }

  :deep(.van-cell-group) {
    border-radius: 12px;
    overflow: hidden;
  }

  :deep(.van-cell) {
    font-size: 14px;

    .van-cell__title {
      color: #666;
    }

    .van-cell__value {
      color: #333;
    }
  }

  .skills-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    justify-content: flex-end;
  }

  .introduction {
    font-size: 14px;
    color: #666;
    line-height: 1.8;
    padding: 8px 0;
    word-break: break-all;
  }
}

// 证件网格
.cert-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 0 16px;

  .cert-item {
    cursor: pointer;
    transition: transform 0.2s;

    &:active {
      transform: scale(0.95);
    }

    .cert-image {
      width: 100%;
      height: 100px;
      border-radius: 8px;
      overflow: hidden;
      background: #F7F8FA;
      border: 1px solid #EBEDF0;
    }

    .cert-label {
      font-size: 12px;
      color: #666;
      text-align: center;
      margin-top: 6px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
}

// 底部操作区
.action-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px;
  background: #fff;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;

  .action-btn {
    height: 48px;
    font-size: 16px;
    font-weight: bold;

    &.reject-btn {
      background: #fff;
      border: 1px solid #EE0A24;
      color: #EE0A24;

      &:active {
        background: #FFF1F0;
      }
    }

    &.approve-btn {
      background: linear-gradient(135deg, #07C160 0%, #06AE56 100%);
      border: none;
      box-shadow: 0 4px 12px rgba(7, 193, 96, 0.3);

      &:active {
        opacity: 0.8;
      }
    }
  }
}

// 拒绝对话框
.reject-dialog-content {
  padding: 16px;

  :deep(.van-field) {
    background: #F7F8FA;
    border-radius: 8px;
    padding: 12px;
  }
}
</style>
