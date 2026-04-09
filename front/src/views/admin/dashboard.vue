<script setup lang="ts">
import { showToast } from 'vant'
import apiAdmin from '@/api/modules/admin'

definePage({
  name: 'admin-dashboard',
  meta: {
    title: '数据统计',
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
const statistics = ref<any>(null)

// 获取统计数据
async function getStatistics() {
  loading.value = true
  try {
    const res = await apiAdmin.getStatistics()

    if (res.code === 200) {
      statistics.value = res.data
    }
  }
  catch (error: any) {
    showToast(error.message || '加载失败')
  }
  finally {
    loading.value = false
  }
}

// 下拉刷新
async function onRefresh() {
  await getStatistics()
}

// 跳转到对应管理页面
function goToPage(path: string) {
  router.push(path)
}

onMounted(() => {
  getStatistics()
})
</script>

<template>
  <div class="admin-dashboard-page">
    <van-nav-bar
      title="数据统计"
      left-arrow
      @click-left="router.back()"
      class="nav-bar"
    />

    <van-pull-refresh v-model="loading" @refresh="onRefresh">
      <div v-if="statistics" class="content">
        <!-- 用户统计 -->
        <div class="stats-section">
          <div class="section-header">
            <van-icon name="friends-o" size="18" color="#1989FA" />
            <span>用户统计</span>
            <van-button
              size="mini"
              plain
              @click="goToPage('/admin/users')"
            >
              查看详情
            </van-button>
          </div>

          <div class="stats-grid">
            <div class="stat-card primary">
              <div class="stat-value">{{ statistics.users.total }}</div>
              <div class="stat-label">总用户数</div>
            </div>
            <div class="stat-card success">
              <div class="stat-value">{{ statistics.users.active }}</div>
              <div class="stat-label">活跃用户</div>
            </div>
            <div class="stat-card warning">
              <div class="stat-value">{{ statistics.users.today }}</div>
              <div class="stat-label">今日新增</div>
            </div>
            <div class="stat-card info">
              <div class="stat-value">{{ statistics.users.month }}</div>
              <div class="stat-label">本月新增</div>
            </div>
          </div>

          <!-- 角色分布 -->
          <div class="role-distribution">
            <div class="role-item">
              <span class="role-label">普通用户</span>
              <span class="role-value">{{ statistics.users.role_distribution.user }}</span>
            </div>
            <div class="role-item">
              <span class="role-label">家政阿姨</span>
              <span class="role-value">{{ statistics.users.role_distribution.worker }}</span>
            </div>
            <div class="role-item">
              <span class="role-label">管理员</span>
              <span class="role-value">{{ statistics.users.role_distribution.admin }}</span>
            </div>
          </div>
        </div>

        <!-- 阿姨统计 -->
        <div class="stats-section">
          <div class="section-header">
            <van-icon name="user-o" size="18" color="#07C160" />
            <span>阿姨统计</span>
            <van-button
              size="mini"
              plain
              @click="goToPage('/admin/workers')"
            >
              查看详情
            </van-button>
          </div>

          <div class="stats-grid">
            <div class="stat-card primary">
              <div class="stat-value">{{ statistics.workers.total }}</div>
              <div class="stat-label">总阿姨数</div>
            </div>
            <div class="stat-card success">
              <div class="stat-value">{{ statistics.workers.available }}</div>
              <div class="stat-label">在线接单</div>
            </div>
            <div class="stat-card warning">
              <div class="stat-value">{{ statistics.workers.today }}</div>
              <div class="stat-label">今日新增</div>
            </div>
            <div class="stat-card info">
              <div class="stat-value">{{ statistics.workers.avg_rating }}</div>
              <div class="stat-label">平均评分</div>
            </div>
          </div>
        </div>

        <!-- 申请统计 -->
        <div class="stats-section">
          <div class="section-header">
            <van-icon name="todo-list-o" size="18" color="#FF9F43" />
            <span>申请统计</span>
            <van-button
              size="mini"
              plain
              @click="goToPage('/admin/applications')"
            >
              查看详情
            </van-button>
          </div>

          <div class="stats-grid">
            <div class="stat-card warning">
              <div class="stat-value">{{ statistics.applications.pending }}</div>
              <div class="stat-label">待审核</div>
            </div>
            <div class="stat-card success">
              <div class="stat-value">{{ statistics.applications.approved }}</div>
              <div class="stat-label">已通过</div>
            </div>
            <div class="stat-card danger">
              <div class="stat-value">{{ statistics.applications.rejected }}</div>
              <div class="stat-label">已拒绝</div>
            </div>
            <div class="stat-card info">
              <div class="stat-value">{{ statistics.applications.today }}</div>
              <div class="stat-label">今日申请</div>
            </div>
          </div>

          <!-- 总申请数 -->
          <div class="total-applications">
            <span class="total-label">总申请数</span>
            <span class="total-value">{{ statistics.applications.total }}</span>
          </div>
        </div>

        <!-- 快捷操作 -->
        <div class="quick-actions">
          <div class="action-title">快捷操作</div>
          <van-grid :column-num="4" :border="false">
            <van-grid-item
              icon="friends-o"
              text="用户管理"
              @click="goToPage('/admin/users')"
            />
            <van-grid-item
              icon="user-o"
              text="阿姨管理"
              @click="goToPage('/admin/workers')"
            />
            <van-grid-item
              icon="todo-list-o"
              text="申请审核"
              @click="goToPage('/admin/applications')"
            />
            <van-grid-item
              icon="volume-o"
              text="公告管理"
              @click="goToPage('/admin/announcements')"
            />
          </van-grid>
          <van-grid :column-num="4" :border="false" style="margin-top: -8px;">
            <van-grid-item
              icon="bar-chart-o"
              text="数据中心"
              @click="goToPage('/admin/data-center')"
            />
          </van-grid>
        </div>
      </div>
    </van-pull-refresh>
  </div>
</template>

<style scoped lang="scss">
.admin-dashboard-page {
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

.content {
  padding: 16px;
}

// 统计区域
.stats-section {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  .section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    font-size: 16px;
    font-weight: bold;
    color: #333;

    > span {
      flex: 1;
    }

    :deep(.van-button) {
      height: 24px;
      padding: 0 12px;
      font-size: 12px;
    }
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 16px;

    .stat-card {
      padding: 16px;
      border-radius: 8px;
      text-align: center;

      &.primary {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);

        .stat-value {
          color: #1989FA;
        }
      }

      &.success {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);

        .stat-value {
          color: #07C160;
        }
      }

      &.warning {
        background: linear-gradient(135deg, #FFF7E6 0%, #FFE7BA 100%);

        .stat-value {
          color: #FF9F43;
        }
      }

      &.info {
        background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%);

        .stat-value {
          color: #9C27B0;
        }
      }

      &.danger {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);

        .stat-value {
          color: #EE0A24;
        }
      }

      .stat-value {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 4px;
      }

      .stat-label {
        font-size: 13px;
        color: #666;
      }
    }
  }

  // 角色分布
  .role-distribution {
    padding-top: 12px;
    border-top: 1px solid #F5F7FA;

    .role-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      font-size: 14px;

      .role-label {
        color: #666;
      }

      .role-value {
        color: #333;
        font-weight: 500;
      }
    }
  }

  // 总申请数
  .total-applications {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: #F7F8FA;
    border-radius: 8px;
    font-size: 15px;

    .total-label {
      color: #666;
    }

    .total-value {
      color: #333;
      font-size: 20px;
      font-weight: bold;
    }
  }
}

// 快捷操作
.quick-actions {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  .action-title {
    font-size: 16px;
    font-weight: bold;
    color: #333;
    margin-bottom: 12px;
  }

  :deep(.van-grid-item) {
    .van-grid-item__content {
      padding: 16px 8px;
    }

    .van-grid-item__icon {
      font-size: 28px;
      color: #FF9F43;
    }

    .van-grid-item__text {
      margin-top: 8px;
      color: #666;
      font-size: 13px;
    }
  }
}
</style>
