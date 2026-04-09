<script setup lang="ts">
import { showToast } from 'vant'
import apiWorker from '@/api/modules/worker'

definePage({
  name: 'worker-center',
  meta: {
    title: '阿姨工作台',
  },
})

const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const profile = ref<any>(null)
const myServices = ref<any[]>([])

// 菜单项
const menuItems = [
  {
    icon: 'edit',
    title: '编辑资料',
    desc: '修改个人信息、技能标签',
    path: '/worker/profile-edit',
    color: '#FF9F43',
  },
  {
    icon: 'bill-o',
    title: '订单管理',
    desc: '查看和处理预约订单',
    path: '/worker/orders',
    color: '#7232dd',
  },
  {
    icon: 'clock-o',
    title: '时间管理',
    desc: '设置可预约时间段',
    path: '/worker/schedule',
    color: '#4CAF50',
  },
  {
    icon: 'orders-o',
    title: '服务管理',
    desc: '设置提供的服务和价格',
    path: '/worker/my-services',
    color: '#2196F3',
  },
  {
    icon: 'comment-o',
    title: '我的评价',
    desc: '查看用户对我的评价',
    path: '/worker/reviews',
    color: '#FF9F43',
  },
]

// 获取档案信息
async function getProfile() {
  loading.value = true
  try {
    const res: any = await apiWorker.getMyProfile()
    if (res.code === 200) {
      profile.value = res.data
    }
  }
  catch (error: any) {
    console.error('获取档案失败:', error)
    if (error.response?.status === 404 || error.response?.status === 403) {
      showToast('您还不是家政阿姨')
      router.replace('/user/center')
    }
  }
  finally {
    loading.value = false
  }
}

// 获取我的服务
async function getMyServices() {
  try {
    const res: any = await apiWorker.getMyServices()
    if (res.code === 200) {
      myServices.value = res.data || []
    }
  }
  catch (error) {
    console.error('获取服务失败:', error)
  }
}

// 切换接单状态
async function toggleAvailable() {
  if (!profile.value)
    return
  const newStatus = !profile.value.is_available
  try {
    const res: any = await apiWorker.updateMyProfile({
      is_available: newStatus,
    })
    if (res.code === 200) {
      profile.value.is_available = newStatus
      showToast(newStatus ? '已开启接单' : '已暂停接单')
    }
  }
  catch (error) {
    showToast('操作失败')
  }
}

// 跳转
function goTo(path: string) {
  router.push(path)
}

onMounted(() => {
  getProfile()
  getMyServices()
})
</script>

<template>
  <div class="worker-center">
    <!-- 头部信息 -->
    <div class="header-section">
      <div v-if="loading" class="loading-placeholder">
        <van-loading color="#fff" />
      </div>
      <template v-else-if="profile">
        <div class="profile-card">
          <van-image
            round
            width="70"
            height="70"
            :src="profile.id_card_front"
            fit="cover"
            class="avatar"
          >
            <template #error>
              <div class="avatar-placeholder">
                <van-icon name="user-o" size="35" color="#ccc" />
              </div>
            </template>
          </van-image>
          <div class="info">
            <div class="name-row">
              <span class="name">{{ profile.real_name }}</span>
              <van-tag v-if="profile.is_available" type="success" size="medium">
                接单中
              </van-tag>
              <van-tag v-else type="default" size="medium">
                暂停接单
              </van-tag>
            </div>
            <div class="rating-row">
              <van-rate
                :model-value="profile.rating || 5"
                :size="14"
                color="#FFD700"
                void-color="#ddd"
                readonly
                allow-half
              />
              <span class="rating-text">{{ profile.rating || 5.0 }}</span>
            </div>
            <div class="stats-row">
              <span>完成订单：{{ profile.completed_orders || 0 }}单</span>
              <span v-if="profile.hourly_rate">时薪：¥{{ profile.hourly_rate }}/时</span>
            </div>
          </div>
        </div>
        <!-- 接单开关 -->
        <div class="switch-row">
          <span>接单状态</span>
          <van-switch
            :model-value="profile.is_available"
            size="24"
            active-color="#4CAF50"
            @update:model-value="toggleAvailable"
          />
        </div>
      </template>
    </div>

    <!-- 数据统计 -->
    <div v-if="profile" class="stats-section">
      <div class="stat-item">
        <span class="value">{{ profile.total_orders || 0 }}</span>
        <span class="label">总订单</span>
      </div>
      <div class="stat-item">
        <span class="value">{{ profile.completed_orders || 0 }}</span>
        <span class="label">已完成</span>
      </div>
      <div class="stat-item">
        <span class="value">{{ myServices.length }}</span>
        <span class="label">服务项目</span>
      </div>
      <div class="stat-item">
        <span class="value">{{ profile.experience_years || 0 }}</span>
        <span class="label">工作年限</span>
      </div>
    </div>

    <!-- 功能菜单 -->
    <div class="menu-section">
      <div class="section-title">
        工作台
      </div>
      <div class="menu-list">
        <div
          v-for="item in menuItems"
          :key="item.path"
          class="menu-item"
          @click="goTo(item.path)"
        >
          <div class="icon-wrapper" :style="{ backgroundColor: `${item.color}20` }">
            <van-icon :name="item.icon" :color="item.color" size="24" />
          </div>
          <div class="content">
            <div class="title">
              {{ item.title }}
            </div>
            <div class="desc">
              {{ item.desc }}
            </div>
          </div>
          <van-icon name="arrow" color="#ccc" />
        </div>
      </div>
    </div>

    <!-- 技能标签 -->
    <div v-if="profile?.skills?.length" class="skills-section">
      <div class="section-title">
        我的技能
      </div>
      <div class="skills-list">
        <van-tag
          v-for="skill in profile.skills"
          :key="skill"
          plain
          type="primary"
          size="medium"
        >
          {{ skill }}
        </van-tag>
      </div>
    </div>

    <!-- 底部导航 -->
    <van-tabbar route active-color="#FF9F43" inactive-color="#999">
      <van-tabbar-item to="/" icon="home-o">
        首页
      </van-tabbar-item>
      <van-tabbar-item to="/worker/center" icon="manager-o">
        工作台
      </van-tabbar-item>
      <van-tabbar-item to="/user/center" icon="user-o">
        我的
      </van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped lang="scss">
.worker-center {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 70px;
}

.header-section {
  background: linear-gradient(135deg, #FF9F43, #FF7F50);
  padding: 20px 16px;
  padding-top: calc(20px + env(safe-area-inset-top));

  .loading-placeholder {
    display: flex;
    justify-content: center;
    padding: 40px 0;
  }

  .profile-card {
    display: flex;
    gap: 16px;

    .avatar {
      flex-shrink: 0;
      border: 3px solid rgba(255, 255, 255, 0.3);
    }

    .avatar-placeholder {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f5f5f5;
    }

    .info {
      flex: 1;
      color: #fff;

      .name-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        .name {
          font-size: 20px;
          font-weight: bold;
        }
      }

      .rating-row {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 6px;

        .rating-text {
          font-size: 14px;
          font-weight: 500;
        }
      }

      .stats-row {
        font-size: 13px;
        opacity: 0.9;
        display: flex;
        gap: 12px;
      }
    }
  }

  .switch-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    color: #fff;
    font-size: 15px;
  }
}

.stats-section {
  display: flex;
  background: #fff;
  margin: 12px 16px;
  border-radius: 12px;
  padding: 16px 0;

  .stat-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    border-right: 1px solid #f0f0f0;

    &:last-child {
      border-right: none;
    }

    .value {
      font-size: 20px;
      font-weight: bold;
      color: #333;
    }

    .label {
      font-size: 12px;
      color: #999;
    }
  }
}

.menu-section {
  background: #fff;
  margin: 12px 16px;
  border-radius: 12px;
  padding: 16px;

  .section-title {
    font-size: 16px;
    font-weight: bold;
    color: #333;
    margin-bottom: 12px;
  }

  .menu-list {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .menu-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      background: #fafafa;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.2s;

      &:active {
        background: #f0f0f0;
      }

      .icon-wrapper {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
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

.skills-section {
  background: #fff;
  margin: 12px 16px;
  border-radius: 12px;
  padding: 16px;

  .section-title {
    font-size: 16px;
    font-weight: bold;
    color: #333;
    margin-bottom: 12px;
  }

  .skills-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>
