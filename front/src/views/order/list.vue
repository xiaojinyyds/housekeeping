<script setup lang="ts">
import { showToast, showDialog } from 'vant'
import { useRouter, useRoute } from 'vue-router'
import apiAppointment from '@/api/modules/appointment'

definePage({
  name: 'order-list',
  meta: {
    title: '我的订单',
    auth: true,
  },
})

import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const active = ref('/order/list')

const currentRole = ref('user') // user-雇主, worker-阿姨
const activeTab = ref(route.query.status as string || '')
const list = ref<any[]>([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)

const tabs = [
  { title: '全部', name: '' },
  { title: '待接单', name: 'pending' },
  { title: '进行中', name: 'in_progress' }, // 包含 accepted
  { title: '待评价', name: 'completed' },
  { title: '已取消', name: 'cancelled' },
]

async function onLoad() {
  if (refreshing.value) {
    list.value = []
    refreshing.value = false
  }

  try {
    const res: any = await apiAppointment.getMyAppointments({
      status: activeTab.value === 'in_progress' ? undefined : activeTab.value,
      role: currentRole.value,
      page: page.value,
      page_size: 10
    })
    
    if (res.code === 200) {
      if (page.value === 1) {
        list.value = res.data.list
      } else {
        list.value = [...list.value, ...res.data.list]
      }
      
      finished.value = list.value.length >= res.data.total
      page.value++
    }
  } catch (error) {
    finished.value = true
  } finally {
    loading.value = false
  }
}

function onRefresh() {
  finished.value = false
  page.value = 1
  loading.value = true
  onLoad()
}

function onTabChange(name: string) {
  activeTab.value = name
  onRefresh()
}

// 状态映射
const statusMap: Record<string, { text: string, color: string }> = {
  'pending': { text: '待接单', color: '#FF9F43' },
  'accepted': { text: '已接单', color: '#1989FA' },
  'in_progress': { text: '服务中', color: '#07C160' },
  'rejected': { text: '已拒绝', color: '#EE0A24' },
  'completed': { text: '待评价', color: '#07C160' },
  'reviewed': { text: '已完成', color: '#999' },
  'cancelled': { text: '已取消', color: '#999' }
}

function getStatusText(status: string) {
  return statusMap[status]?.text || status
}

function getStatusColor(status: string) {
  return statusMap[status]?.color || '#999'
}

// 取消订单
async function handleCancel(order: any) {
  showDialog({
    title: '提示',
    message: '确定要取消该订单吗？',
    showCancelButton: true,
  }).then(async (action) => {
    if (action === 'confirm') {
      try {
        await apiAppointment.cancelAppointment(order.id, { reason: '用户主动取消' })
        showToast('取消成功')
        onRefresh()
      } catch (error) {
        showToast('取消失败')
      }
    }
  })
}

// 去评价
function handleReview(order: any) {
  router.push(`/order/review/${order.id}`)
}

// 支付（模拟）
function handlePay(order: any) {
  showToast('支付功能开发中')
}

// 去详情
function goDetail(order: any) {
  // router.push(`/order/detail/${order.id}`)
}

</script>

<template>
  <div class="order-list-page">
    <van-nav-bar title="我的订单" left-arrow fixed placeholder @click-left="router.back()" />
    
    <!-- 角色切换 (仅阿姨可见) -->
    <div v-if="userStore.isWorker" class="role-switch">
      <van-tabs v-model:active="currentRole" type="card" @change="onTabChange(activeTab)" color="#FF9F43" style="margin: 10px 0;">
        <van-tab title="我点的单" name="user"></van-tab>
        <van-tab title="我的接单" name="worker"></van-tab>
      </van-tabs>
    </div>

    <van-tabs v-model:active="activeTab" sticky :offset-top="userStore.isWorker ? 90 : 46" @change="onTabChange" color="#FF9F43">
      <van-tab v-for="tab in tabs" :key="tab.name" :title="tab.title" :name="tab.name">
        <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
          <van-list
            v-model:loading="loading"
            :finished="finished"
            finished-text="没有更多了"
            @load="onLoad"
            class="list-content"
          >
            <div v-for="order in list" :key="order.id" class="order-card" @click="goDetail(order)">
              <div class="header">
                <span class="order-no">订单号：{{ order.order_no }}</span>
                <span class="status" :style="{ color: getStatusColor(order.status) }">
                  {{ getStatusText(order.status) }}
                </span>
              </div>
              
              <div class="content">
                <van-image
                  width="60"
                  height="60"
                  radius="4"
                  src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
                  class="thumb"
                />
                <div class="info">
                  <div class="name">{{ order.service_name }}</div>
                  <div class="desc">
                    <div v-if="currentRole === 'user'">预约阿姨：{{ order.worker_name }}</div>
                    <div v-else>联系人：{{ order.contact_name }} ({{ order.contact_phone }})</div>
                    <div>预约时间：{{ order.appointment_date }} {{ order.time_slot_name }}</div>
                  </div>
                </div>
                <div class="price">
                  <div class="total">¥{{ order.total_price }}</div>
                  <div class="unit">共{{ order.duration_hours }}小时</div>
                </div>
              </div>
              
              <div class="footer">
                <div class="actions">
                  <van-button 
                    v-if="order.status === 'pending' || order.status === 'accepted'" 
                    size="small" 
                    round 
                    @click.stop="handleCancel(order)"
                  >
                    取消订单
                  </van-button>
                  
                  <van-button 
                    v-if="order.status === 'completed'" 
                    size="small" 
                    round 
                    plain
                    color="#FF9F43"
                    @click.stop="handleReview(order)"
                  >
                    去评价
                  </van-button>
                  
                  <van-button 
                    v-if="order.status === 'pending'" 
                    size="small" 
                    round 
                    color="#FF9F43"
                    @click.stop="handlePay(order)"
                  >
                    立即付款
                  </van-button>
                </div>
              </div>
            </div>
            
            <van-empty v-if="!loading && list.length === 0" description="暂无订单" />
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>

    <!-- 底部导航 -->
    <van-tabbar v-model="active" route active-color="#FF9F43" inactive-color="#999">
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
.order-list-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.list-content {
  padding: 12px 16px;
}

.order-card {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #f9f9f9;
    
    .order-no {
      color: #999;
    }
    
    .status {
      font-weight: bold;
    }
  }
  
  .content {
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
    
    .thumb {
      flex-shrink: 0;
    }
    
    .info {
      flex: 1;
      
      .name {
        font-size: 15px;
        font-weight: bold;
        margin-bottom: 6px;
      }
      
      .desc {
        font-size: 12px;
        color: #666;
        line-height: 1.5;
      }
    }
    
    .price {
      text-align: right;
      
      .total {
        font-size: 16px;
        font-weight: bold;
        color: #333;
      }
      
      .unit {
        font-size: 12px;
        color: #999;
        margin-top: 2px;
      }
    }
  }
  
  .footer {
    display: flex;
    justify-content: flex-end;
    
    .actions {
      display: flex;
      gap: 8px;
    }
  }
}
</style>
