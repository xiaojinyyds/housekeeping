<script setup lang="ts">
import { showToast, showDialog } from 'vant'
import apiWorker from '@/api/modules/worker'

definePage({
  name: 'admin-applications',
  meta: {
    title: '申请审核',
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
const applicationList = ref<any[]>([])
const page = ref(1)
const pageSize = 10

// 筛选状态
const activeTab = ref('pending')
const tabs = [
  { name: 'pending', title: '待审核' },
  { name: 'approved', title: '已通过' },
  { name: 'rejected', title: '已拒绝' },
]

// 获取申请列表
async function getApplications(isRefresh = false) {
  if (isRefresh) {
    page.value = 1
    applicationList.value = []
    finished.value = false
  }

  loading.value = true
  try {
    const res = await apiWorker.getApplications({
      status: activeTab.value,
      page: page.value,
      page_size: pageSize,
    })

    if (res.code === 200) {
      if (isRefresh) {
        applicationList.value = res.data.list
      }
      else {
        applicationList.value.push(...res.data.list)
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
  getApplications(true)
}

// 下拉刷新
async function onRefresh() {
  await getApplications(true)
}

// 上拉加载
async function onLoad() {
  await getApplications()
}

// 查看详情
function viewDetail(application: any) {
  router.push(`/admin/application-detail/${application.id}`)
}

// 通过申请
async function approveApplication(application: any) {
  try {
    await showDialog({
      title: '确认通过',
      message: `确定通过 ${application.real_name} 的申请吗？`,
    })

    const res = await apiWorker.reviewApplication(application.id, {
      status: 'approved',
    })

    if (res.code === 200) {
      showToast('审核通过')
      getApplications(true)
    }
  }
  catch (error: any) {
    if (error !== 'cancel') {
      showToast(error.message || '操作失败')
    }
  }
}

// 拒绝申请
async function rejectApplication(application: any) {
  showRejectDialog.value = true
  currentApplication.value = application
}

// 拒绝对话框
const showRejectDialog = ref(false)
const currentApplication = ref<any>(null)
const rejectReason = ref('')

// 确认拒绝
async function confirmReject() {
  if (!rejectReason.value.trim()) {
    showToast('请输入拒绝原因')
    return
  }

  try {
    const res = await apiWorker.reviewApplication(currentApplication.value.id, {
      status: 'rejected',
      reject_reason: rejectReason.value,
    })

    if (res.code === 200) {
      showToast('已拒绝')
      showRejectDialog.value = false
      rejectReason.value = ''
      getApplications(true)
    }
  }
  catch (error: any) {
    showToast(error.message || '操作失败')
  }
}

// 统计数据
const stats = ref({
  pending: 0,
  approved: 0,
  rejected: 0,
})

// 获取统计数据
async function getStats() {
  try {
    const [pendingRes, approvedRes, rejectedRes] = await Promise.all([
      apiWorker.getApplications({ status: 'pending', page: 1, page_size: 1 }),
      apiWorker.getApplications({ status: 'approved', page: 1, page_size: 1 }),
      apiWorker.getApplications({ status: 'rejected', page: 1, page_size: 1 }),
    ])

    if (pendingRes.code === 200)
      stats.value.pending = pendingRes.data.total
    if (approvedRes.code === 200)
      stats.value.approved = approvedRes.data.total
    if (rejectedRes.code === 200)
      stats.value.rejected = rejectedRes.data.total
  }
  catch (error) {
    console.error('获取统计数据失败', error)
  }
}

onMounted(() => {
  getApplications(true)
  getStats()
})
</script>

<template>
  <div class="admin-applications-page">
    <van-nav-bar
      title="申请审核"
      left-arrow
      @click-left="router.back()"
      class="nav-bar"
    />

    <!-- 统计看板 -->
    <div class="dashboard-section">
      <div class="stat-card">
        <div class="stat-icon pending">
          <van-icon name="clock-o" size="20" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待审核</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon approved">
          <van-icon name="success" size="20" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.approved }}</div>
          <div class="stat-label">已通过</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon rejected">
          <van-icon name="cross" size="20" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.rejected }}</div>
          <div class="stat-label">已拒绝</div>
        </div>
      </div>
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
            <div class="application-list">
              <div
                v-for="application in applicationList"
                :key="application.id"
                class="application-card"
              >
                <!-- 卡片头部 -->
                <div class="card-header">
                  <!-- 左侧头像 -->
                  <div class="avatar-wrapper">
                    <div class="avatar">
                      {{ application.real_name.charAt(0) }}
                    </div>
                  </div>

                  <!-- 中间信息 -->
                  <div class="applicant-info">
                    <div class="applicant-name">
                      {{ application.real_name }}
                    </div>
                    <div class="applicant-meta">
                      <span>{{ application.gender === 'female' ? '女' : '男' }}</span>
                      <span class="divider">|</span>
                      <span>{{ application.age }}岁</span>
                      <span class="divider">|</span>
                      <span>{{ application.experience_years }}年经验</span>
                    </div>
                  </div>

                  <!-- 右侧状态 -->
                  <van-tag
                    v-if="application.status === 'pending'"
                    plain
                    color="#FF9F43"
                  >
                    待审核
                  </van-tag>
                  <van-tag
                    v-else-if="application.status === 'approved'"
                    plain
                    color="#07C160"
                  >
                    已通过
                  </van-tag>
                  <van-tag
                    v-else
                    plain
                    color="#EE0A24"
                  >
                    已拒绝
                  </van-tag>
                </div>

                <!-- 卡片内容 -->
                <div class="card-body">
                  <div class="info-item">
                    <van-icon name="phone-o" size="14" color="#999" />
                    <span class="info-text">{{ application.phone }}</span>
                  </div>
                  <div class="info-item">
                    <van-icon name="location-o" size="14" color="#999" />
                    <span class="info-text">{{ application.address }}</span>
                  </div>
                  <div class="info-item skills">
                    <van-icon name="star-o" size="14" color="#999" />
                    <div class="skills-tags">
                      <van-tag
                        v-for="skill in application.skills"
                        :key="skill"
                        plain
                        size="mini"
                        color="#1989FA"
                      >
                        {{ skill }}
                      </van-tag>
                    </div>
                  </div>

                  <!-- 拒绝原因 -->
                  <div v-if="application.status === 'rejected' && application.reject_reason" class="reject-box">
                    <van-icon name="info-o" size="14" color="#FF9F43" />
                    <span class="reject-text">{{ application.reject_reason }}</span>
                  </div>
                </div>

                <!-- 卡片底部 -->
                <div class="card-footer">
                  <div class="apply-time">
                    {{ new Date(application.created_at).toLocaleDateString() }}
                  </div>
                  <div class="action-buttons">
                    <van-button
                      size="small"
                      round
                      plain
                      @click="viewDetail(application)"
                    >
                      查看详情
                    </van-button>
                    <van-button
                      v-if="application.status === 'pending'"
                      size="small"
                      round
                      plain
                      color="#EE0A24"
                      @click="rejectApplication(application)"
                    >
                      拒绝
                    </van-button>
                    <van-button
                      v-if="application.status === 'pending'"
                      size="small"
                      round
                      type="success"
                      @click="approveApplication(application)"
                    >
                      通过
                    </van-button>
                  </div>
                </div>
              </div>
            </div>
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>

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
.admin-applications-page {
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

// 统计看板
.dashboard-section {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #F7F8FA;

  .stat-card {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 12px;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

    .stat-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;

      &.pending {
        background: #FFF7E6;
        color: #FF9F43;
      }

      &.approved {
        background: #E8F5E9;
        color: #07C160;
      }

      &.rejected {
        background: #FFEBEE;
        color: #EE0A24;
      }
    }

    .stat-info {
      flex: 1;
      min-width: 0;

      .stat-value {
        font-size: 22px;
        font-weight: bold;
        color: #333;
        line-height: 1.2;
        margin-bottom: 2px;
      }

      .stat-label {
        font-size: 12px;
        color: #999;
      }
    }
  }
}

.application-list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;

  .application-card {
    background: #fff;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

    // 卡片头部
    .card-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;

      .avatar-wrapper {
        flex-shrink: 0;

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
      }

      .applicant-info {
        flex: 1;
        min-width: 0;

        .applicant-name {
          font-size: 16px;
          font-weight: bold;
          color: #333;
          margin-bottom: 4px;
        }

        .applicant-meta {
          font-size: 13px;
          color: #999;

          .divider {
            margin: 0 6px;
            color: #DCDEE0;
          }
        }
      }
    }

    // 卡片内容
    .card-body {
      margin-bottom: 16px;

      .info-item {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        margin-bottom: 10px;
        font-size: 14px;

        &:last-child {
          margin-bottom: 0;
        }

        .info-text {
          flex: 1;
          color: #666;
          line-height: 1.5;
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

      .reject-box {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        margin-top: 12px;
        padding: 10px 12px;
        background: #FFF7E6;
        border-radius: 8px;
        border-left: 3px solid #FF9F43;

        .reject-text {
          flex: 1;
          font-size: 13px;
          color: #FF9F43;
          line-height: 1.5;
        }
      }
    }

    // 卡片底部
    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 12px;
      border-top: 1px solid #F5F7FA;

      .apply-time {
        font-size: 12px;
        color: #BFBFBF;
      }

      .action-buttons {
        display: flex;
        gap: 8px;

        :deep(.van-button) {
          height: 32px;
          padding: 0 16px;
          font-size: 13px;
        }
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
