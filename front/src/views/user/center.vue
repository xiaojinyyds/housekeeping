<script setup lang="ts">
import { showConfirmDialog, showToast, showLoadingToast } from 'vant'
import apiWorker from '@/api/modules/worker'

definePage({
  name: 'user-center',
  meta: {
    title: '个人中心',
    auth: true,
  },
})

const router = useRouter()
const userStore = useUserStore()

const active = ref(2)

// 用户资产数据（模拟）
const userAssets = reactive({
  balance: 0,
  coupons: 0,
  points: 0,
})

// 订单状态数据（模拟）
const orderStats = [
  { icon: 'pending-payment', label: '待付款', count: 0, path: '/order/list?status=pending' },
  { icon: 'clock-o', label: '待服务', count: 0, path: '/order/list?status=accepted' },
  { icon: 'service-o', label: '服务中', count: 0, path: '/order/list?status=in_progress' },
  { icon: 'comment-o', label: '待评价', count: 0, path: '/order/list?status=completed' },
]

// 管理员功能菜单
const adminMenuItems = [
  {
    icon: 'todo-list-o',
    iconColor: '#FF9F43',
    title: '申请审核',
    path: '/admin/applications',
    badge: 0,
  },
  {
    icon: 'friends-o',
    iconColor: '#07C160',
    title: '阿姨管理',
    path: '/admin/workers',
  },
  {
    icon: 'manager-o',
    iconColor: '#1989FA',
    title: '用户管理',
    path: '/admin/users',
  },
  {
    icon: 'volume-o',
    iconColor: '#9C27B0',
    title: '公告管理',
    path: '/admin/announcements',
  },
  {
    icon: 'chart-trending-o',
    iconColor: '#FF976A',
    title: '数据统计',
    path: '/admin/dashboard',
  },
]

// 阿姨功能菜单
const workerMenuItems = [
  {
    icon: 'manager-o',
    iconColor: '#FF9F43',
    title: '阿姨工作台',
    desc: '管理时间、服务和接单',
    path: '/worker/center',
  },
  {
    icon: 'edit',
    iconColor: '#4CAF50',
    title: '编辑资料',
    desc: '修改个人信息和技能',
    path: '/worker/profile-edit',
  },
  {
    icon: 'clock-o',
    iconColor: '#2196F3',
    title: '时间管理',
    desc: '设置可预约时间段',
    path: '/worker/schedule',
  },
  {
    icon: 'orders-o',
    iconColor: '#9C27B0',
    title: '服务管理',
    desc: '设置服务项目和定价',
    path: '/worker/my-services',
  },
]

// 常用功能菜单
const menuItems = [
  {
    icon: 'location-o',
    iconColor: '#1989FA',
    title: '地址管理',
    path: '/user/address',
    show: true,
  },
  {
    icon: 'star-o',
    iconColor: '#FF976A',
    title: '我的收藏',
    path: '/user/favorites',
    show: true,
  },
  {
    icon: 'service-o',
    iconColor: '#07C160',
    title: '客服中心',
    path: '/user/service',
    show: true,
  },
  {
    icon: 'info-o',
    iconColor: '#999',
    title: '关于我们',
    path: '/about',
    show: true,
  },
]

// 获取待审核申请数量
async function getPendingCount() {
  if (!userStore.isAdmin) return
  
  try {
    const res = await apiWorker.getApplications({ status: 'pending', page: 1, page_size: 1 })
    if (res.code === 200) {
      adminMenuItems[0].badge = res.data.total
    }
  }
  catch (error) {
    console.error('获取待审核数量失败', error)
  }
}

// 页面加载时获取待审核数量
onMounted(() => {
  getPendingCount()
})

// 跳转设置
function goSettings() {
  router.push('/user/profile')
}

// 跳转订单列表
function goOrders(path?: string) {
  router.push(path || '/order/list')
}

// 跳转申请页面（先检查是否已有申请）
async function goApply() {
  const toast = showLoadingToast({
    message: '加载中...',
    forbidClick: true,
    duration: 0,
  })

  try {
    const res = await apiWorker.getMyApplication()
    toast.close()

    if (res.code === 200 && res.data) {
      // 已有申请记录，跳转到申请状态页面
      router.push('/worker/application-status')
    }
    else {
      // 没有申请记录，跳转到申请表单页面
      router.push('/worker/apply')
    }
  }
  catch (error: any) {
    toast.close()
    // 如果接口报错，默认跳转到申请页面
    router.push('/worker/apply')
  }
}

// 退出登录
async function handleLogout() {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '确定要退出登录吗？',
    })
    userStore.logout()
    showToast('已退出登录')
  }
  catch {
    // 取消
  }
}

// 跳转登录
function goLogin() {
  router.push('/login')
}
</script>

<template>
  <div class="user-center-page">
    <!-- 头部区域 -->
    <div class="header-section">
      <div class="header-bg" />
      
      <div class="user-area">
        <div v-if="userStore.isLogin" class="user-info">
          <!-- 左侧头像 -->
          <div class="user-avatar" @click="goSettings">
            <van-image
              round
              width="64"
              height="64"
              :src="userStore.userAvatar"
              fit="cover"
            />
          </div>

          <!-- 右侧信息 -->
          <div class="user-detail">
            <div class="user-name">
              {{ userStore.userInfo?.nickname || userStore.userInfo?.email?.split('@')[0] || '用户' }}
            </div>
            <div class="user-tag">
              <van-tag
                v-if="userStore.isAdmin"
                round
                color="rgba(255, 255, 255, 0.3)"
                text-color="#fff"
                size="mini"
              >
                管理员
              </van-tag>
              <van-tag
                v-else-if="userStore.isWorker"
                round
                color="rgba(255, 255, 255, 0.3)"
                text-color="#fff"
                size="mini"
              >
                家政阿姨
              </van-tag>
              <van-tag
                v-else
                round
                color="rgba(255, 255, 255, 0.3)"
                text-color="#fff"
                size="mini"
              >
                普通会员
              </van-tag>
            </div>
          </div>

          <!-- 右上角设置 -->
          <div class="settings-icon" @click="goSettings">
            <van-icon name="setting-o" size="20" color="#fff" />
          </div>
        </div>

        <div v-else class="user-login" @click="goLogin">
          <div class="login-avatar">
            <van-icon name="user-o" size="32" color="#fff" />
          </div>
          <div class="login-text">点击登录</div>
        </div>

        <!-- 数据仪表盘 -->
        <div v-if="userStore.isLogin" class="assets-panel">
          <div class="asset-item">
            <div class="asset-value">{{ userAssets.balance }}</div>
            <div class="asset-label">余额</div>
          </div>
          <div class="asset-divider" />
          <div class="asset-item">
            <div class="asset-value">{{ userAssets.coupons }}</div>
            <div class="asset-label">优惠券</div>
          </div>
          <div class="asset-divider" />
          <div class="asset-item">
            <div class="asset-value">{{ userAssets.points }}</div>
            <div class="asset-label">积分</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 订单状态栏 -->
    <div v-if="userStore.isLogin && userStore.userRole === 'user'" class="order-card">
      <div class="card-header">
        <span class="card-title">我的订单</span>
        <span class="card-more" @click="goOrders()">
          全部订单
          <van-icon name="arrow" size="12" />
        </span>
      </div>
      <van-grid :border="false" :column-num="4" class="order-grid">
        <van-grid-item
          v-for="item in orderStats"
          :key="item.label"
          @click="goOrders(item.path)"
        >
          <template #icon>
            <van-badge :content="item.count > 0 ? item.count : ''" :show-zero="false">
              <van-icon :name="item.icon" size="24" color="#666" />
            </van-badge>
          </template>
          <template #text>
            <span class="order-label">{{ item.label }}</span>
          </template>
        </van-grid-item>
      </van-grid>
    </div>

    <!-- 管理员功能区 -->
    <div v-if="userStore.isAdmin" class="admin-section">
      <div class="section-header">
        <van-icon name="shield-o" size="18" color="#FF9F43" />
        <span>管理功能</span>
      </div>
      <van-cell-group :border="false" class="menu-group">
        <van-cell
          v-for="item in adminMenuItems"
          :key="item.path"
          :title="item.title"
          is-link
          @click="router.push(item.path)"
        >
          <template #icon>
            <van-badge :content="item.badge > 0 ? item.badge : ''" :show-zero="false">
              <van-icon :name="item.icon" :color="item.iconColor" size="20" class="menu-icon" />
            </van-badge>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 阿姨功能区 -->
    <div v-if="userStore.isWorker" class="worker-section">
      <div class="section-header">
        <van-icon name="manager-o" size="18" color="#FF9F43" />
        <span>阿姨工作台</span>
      </div>
      <div class="worker-menu-list">
        <div
          v-for="item in workerMenuItems"
          :key="item.path"
          class="worker-menu-item"
          @click="router.push(item.path)"
        >
          <div class="icon-wrapper" :style="{ backgroundColor: `${item.iconColor}15` }">
            <van-icon :name="item.icon" :color="item.iconColor" size="22" />
          </div>
          <div class="content">
            <div class="title">{{ item.title }}</div>
            <div class="desc">{{ item.desc }}</div>
          </div>
          <van-icon name="arrow" color="#ccc" />
        </div>
      </div>
    </div>

    <!-- 招募广告位 -->
    <div v-if="userStore.userRole === 'user'" class="recruit-banner" @click="goApply">
      <div class="banner-content">
        <div class="banner-text">
          <div class="banner-title">招募家政合伙人</div>
          <div class="banner-subtitle">月入过万 · 时间自由</div>
        </div>
        <div class="banner-icon">
          <van-icon name="gold-coin-o" size="40" color="#FFD700" />
        </div>
      </div>
    </div>

    <!-- 常用功能 -->
    <div class="menu-section">
      <van-cell-group :border="false" class="menu-group">
        <van-cell
          v-for="item in menuItems"
          :key="item.path"
          :title="item.title"
          is-link
          @click="router.push(item.path)"
        >
          <template #icon>
            <van-icon :name="item.icon" :color="item.iconColor" size="20" class="menu-icon" />
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 退出登录 -->
    <div v-if="userStore.isLogin" class="logout-section">
      <van-cell-group :border="false" class="menu-group">
        <van-cell
          title="退出登录"
          center
          @click="handleLogout"
        >
          <template #title>
            <span class="logout-text">退出登录</span>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 底部导航 - 管理员专属 -->
    <van-tabbar v-if="userStore.isAdmin" v-model="active" route active-color="#FF9F43" inactive-color="#999">
      <van-tabbar-item to="/" icon="home-o">
        首页
      </van-tabbar-item>
      <van-tabbar-item to="/admin/workers" icon="friends-o">
        阿姨
      </van-tabbar-item>
      <van-tabbar-item to="/admin/users" icon="manager-o">
        用户
      </van-tabbar-item>
      <van-tabbar-item to="/admin/data-center" icon="bar-chart-o">
        数据
      </van-tabbar-item>
      <van-tabbar-item to="/user/center" icon="user-o">
        我的
      </van-tabbar-item>
    </van-tabbar>

    <!-- 底部导航 - 普通用户/阿姨 -->
    <van-tabbar v-else v-model="active" route active-color="#FF9F43" inactive-color="#999">
      <van-tabbar-item to="/" icon="home-o">
        首页
      </van-tabbar-item>
      <van-tabbar-item v-if="userStore.isWorker" to="/worker/center" icon="manager-o">
        工作台
      </van-tabbar-item>
      <van-tabbar-item to="/worker/list" icon="friends-o">
        服务
      </van-tabbar-item>
      <van-tabbar-item to="/order/list" icon="orders-o">
        订单
      </van-tabbar-item>
      <van-tabbar-item to="/user/center" icon="user-o">
        我的
      </van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped lang="scss">
.user-center-page {
  min-height: 100vh;
  background: #F7F8FA;
  padding-bottom: 60px;
}

// 头部区域
.header-section {
  position: relative;
  height: 220px;
  overflow: hidden;

  .header-bg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(to bottom, #FF9F43, #FFC085);
    border-bottom-left-radius: 20px;
    border-bottom-right-radius: 20px;
  }

  .user-area {
    position: relative;
    z-index: 2;
    padding: 20px 16px;

    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      position: relative;
      margin-bottom: 24px;

      .user-avatar {
        flex-shrink: 0;
        cursor: pointer;

        :deep(.van-image) {
          border: 2px solid #fff;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
      }

      .user-detail {
        flex: 1;

        .user-name {
          font-size: 20px;
          font-weight: bold;
          color: #fff;
          margin-bottom: 6px;
        }

        .user-tag {
          :deep(.van-tag) {
            border: none;
          }
        }
      }

      .settings-icon {
        position: absolute;
        top: 0;
        right: 0;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        border-radius: 50%;
        transition: background 0.2s;

        &:active {
          background: rgba(255, 255, 255, 0.2);
        }
      }
    }

    .user-login {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 24px;
      cursor: pointer;

      .login-avatar {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #fff;
      }

      .login-text {
        font-size: 18px;
        color: #fff;
        font-weight: 500;
      }
    }

    .assets-panel {
      display: flex;
      align-items: center;
      justify-content: space-around;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 12px;
      padding: 16px 0;
      backdrop-filter: blur(10px);

      .asset-item {
        flex: 1;
        text-align: center;

        .asset-value {
          font-size: 22px;
          font-weight: bold;
          color: #fff;
          margin-bottom: 4px;
        }

        .asset-label {
          font-size: 12px;
          color: rgba(255, 255, 255, 0.9);
        }
      }

      .asset-divider {
        width: 1px;
        height: 30px;
        background: rgba(255, 255, 255, 0.3);
      }
    }
  }
}

// 订单卡片
.order-card {
  margin: -40px 16px 12px;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 3;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;

    .card-title {
      font-size: 16px;
      font-weight: bold;
      color: #333;
    }

    .card-more {
      font-size: 13px;
      color: #999;
      display: flex;
      align-items: center;
      gap: 4px;
      cursor: pointer;

      &:active {
        opacity: 0.7;
      }
    }
  }

  .order-grid {
    :deep(.van-grid-item__content) {
      padding: 12px 8px;
    }

    .order-label {
      font-size: 13px;
      color: #666;
      margin-top: 6px;
    }
  }
}

// 管理员功能区
.admin-section {
  margin: 0 16px 12px;

  .section-header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 12px 4px 8px;
    font-size: 15px;
    font-weight: bold;
    color: #333;
  }

  .menu-group {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    background: linear-gradient(135deg, #FFF9F0 0%, #FFF 100%);
  }

  :deep(.van-cell) {
    padding: 14px 16px;
    background: transparent;

    &::after {
      border-color: #F5F5F5;
    }

    .van-cell__title {
      font-size: 15px;
      color: #333;
      font-weight: 500;
    }

    .menu-icon {
      margin-right: 12px;
    }

    .van-badge {
      display: inline-block;
    }
  }
}

// 招募广告位
.recruit-banner {
  margin: 0 16px 12px;
  background: linear-gradient(135deg, #2C3E50 0%, #34495E 100%);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(44, 62, 80, 0.3);
  transition: transform 0.2s;

  &:active {
    transform: scale(0.98);
  }

  .banner-content {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .banner-text {
      .banner-title {
        font-size: 18px;
        font-weight: bold;
        color: #fff;
        margin-bottom: 6px;
      }

      .banner-subtitle {
        font-size: 13px;
        color: rgba(255, 255, 255, 0.8);
      }
    }

    .banner-icon {
      width: 60px;
      height: 60px;
      background: rgba(255, 215, 0, 0.2);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}

// 阿姨功能区
.worker-section {
  margin: 0 16px 12px;

  .section-header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 12px 4px 8px;
    font-size: 15px;
    font-weight: bold;
    color: #333;
  }

  .worker-menu-list {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

    .worker-menu-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 16px;
      cursor: pointer;
      border-bottom: 1px solid #f5f5f5;
      transition: background 0.2s;

      &:last-child {
        border-bottom: none;
      }

      &:active {
        background: #f9f9f9;
      }

      .icon-wrapper {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
      }

      .content {
        flex: 1;

        .title {
          font-size: 15px;
          font-weight: 500;
          color: #333;
          margin-bottom: 2px;
        }

        .desc {
          font-size: 12px;
          color: #999;
        }
      }
    }
  }
}

// 菜单区域
.menu-section,
.logout-section {
  margin: 0 16px 12px;

  .menu-group {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }

  :deep(.van-cell) {
    padding: 14px 16px;
    background: #fff;

    &::after {
      border-color: #F5F5F5;
    }

    .van-cell__title {
      font-size: 15px;
      color: #333;
    }

    .menu-icon {
      margin-right: 12px;
    }
  }
}

.logout-section {
  :deep(.van-cell) {
    .logout-text {
      display: block;
      text-align: center;
      color: #EE0A24;
      font-size: 15px;
    }
  }
}
</style>
