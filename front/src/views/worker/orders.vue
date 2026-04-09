<script setup lang="ts">
import { showToast, showDialog } from 'vant'
import { useRouter } from 'vue-router'
import apiAppointment from '@/api/modules/appointment'

definePage({
  name: 'worker-orders',
  meta: {
    title: '订单管理',
    auth: true,
  },
})

const router = useRouter()

const activeTab = ref('')
const list = ref<any[]>([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)

const tabs = [
  { title: '全部', name: '' },
  { title: '待接单', name: 'pending' },
  { title: '已接单', name: 'accepted' }, 
  { title: '服务中', name: 'in_progress' },
  { title: '已完成', name: 'completed' },
]

async function onLoad() {
  if (refreshing.value) {
    list.value = []
    refreshing.value = false
  }

  try {
    const res: any = await apiAppointment.getWorkerOrders({
      status: activeTab.value,
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
  'accepted': { text: '待服务', color: '#1989FA' },
  'in_progress': { text: '服务中', color: '#07C160' },
  'rejected': { text: '已拒绝', color: '#EE0A24' },
  'completed': { text: '已完成', color: '#07C160' },
  'reviewed': { text: '已评价', color: '#999' },
  'cancelled': { text: '用户已取消', color: '#999' }
}

function getStatusText(status: string) {
  return statusMap[status]?.text || status
}

function getStatusColor(status: string) {
  return statusMap[status]?.color || '#999'
}

// 操作方法
async function handleAccept(order: any) {
  showDialog({ title: '接单确认', message: '确定接受该订单吗？', showCancelButton: true })
    .then(async (action) => {
      if (action === 'confirm') {
        try {
          await apiAppointment.acceptOrder(order.id)
          showToast('接单成功')
          onRefresh()
        } catch(e) { showToast('操作失败') }
      }
    })
}

async function handleReject(order: any) {
  showDialog({ title: '拒绝确认', message: '确定拒绝该订单吗？', showCancelButton: true })
    .then(async (action) => {
      if (action === 'confirm') {
        try {
          await apiAppointment.rejectOrder(order.id, { reason: '阿姨暂不方便' })
          showToast('已拒绝')
          onRefresh()
        } catch(e) { showToast('操作失败') }
      }
    })
}

async function handleStart(order: any) {
  showDialog({ title: '开始服务', message: '确认到达并开始服务？', showCancelButton: true })
    .then(async (action) => {
      if (action === 'confirm') {
        try {
          await apiAppointment.startService(order.id)
          showToast('开始服务')
          onRefresh()
        } catch(e) { showToast('操作失败') }
      }
    })
}

async function handleComplete(order: any) {
  showDialog({ title: '完成服务', message: '确认服务已完成？', showCancelButton: true })
    .then(async (action) => {
      if (action === 'confirm') {
        try {
          await apiAppointment.completeService(order.id)
          showToast('服务已完成')
          onRefresh()
        } catch(e) { showToast('操作失败') }
      }
    })
}

function callUser(phone: string) {
  window.location.href = `tel:${phone}`;
}
</script>

<template>
  <div class="worker-orders-page">
    <van-nav-bar title="订单管理" left-arrow fixed placeholder @click-left="router.back()" />
    
    <van-tabs v-model:active="activeTab" sticky @change="onTabChange" color="#7232dd">
      <van-tab v-for="tab in tabs" :key="tab.name" :title="tab.title" :name="tab.name">
        <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
          <van-list
            v-model:loading="loading"
            :finished="finished"
            finished-text="没有更多了"
            @load="onLoad"
            class="list-content"
          >
            <div v-for="order in list" :key="order.id" class="order-card">
              <div class="header">
                <span class="time">{{ order.appointment_date }} {{ order.time_slot_name }}</span>
                <span class="status" :style="{ color: getStatusColor(order.status) }">
                  {{ getStatusText(order.status) }}
                </span>
              </div>
              
              <div class="info-section">
                <div class="row">
                  <span class="label">服务项目：</span>
                  <span class="val">{{ order.service_name }} ({{ order.duration_hours }}小时)</span>
                </div>
                <div class="row">
                  <span class="label">服务地址：</span>
                  <span class="val">{{ order.address }}</span>
                </div>
                <div class="row">
                  <span class="label">联系人：</span>
                  <span class="val">{{ order.contact_name }}</span>
                  <van-icon name="phone-o" color="#1989FA" class="phone-icon" @click.stop="callUser(order.contact_phone)" />
                </div>
                <div class="row" v-if="order.remark">
                  <span class="label">备注：</span>
                  <span class="val">{{ order.remark }}</span>
                </div>
              </div>
              
              <div class="footer">
                <div class="price">预计收益: ¥{{ order.total_price }}</div>
                <div class="actions">
                  <template v-if="order.status === 'pending'">
                    <van-button size="small" round plain type="danger" @click.stop="handleReject(order)">拒绝</van-button>
                    <van-button size="small" round type="primary" @click.stop="handleAccept(order)">接单</van-button>
                  </template>
                  
                  <template v-if="order.status === 'accepted'">
                    <van-button size="small" round color="#07C160" @click.stop="handleStart(order)">开始服务</van-button>
                  </template>
                  
                  <template v-if="order.status === 'in_progress'">
                    <van-button size="small" round color="#7232dd" @click.stop="handleComplete(order)">完成服务</van-button>
                  </template>
                </div>
              </div>
            </div>
            
            <van-empty v-if="!loading && list.length === 0" description="暂无订单" />
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>
  </div>
</template>

<style scoped lang="scss">
.worker-orders-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.list-content {
  padding: 12px;
}

.order-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  
  .header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    font-size: 14px;
    font-weight: bold;
    border-bottom: 1px solid #f9f9f9;
    padding-bottom: 8px;
    
    .time { color: #333; }
  }
  
  .info-section {
    margin-bottom: 12px;
    
    .row {
      display: flex;
      margin-bottom: 6px;
      font-size: 13px;
      line-height: 1.5;
      
      .label {
        color: #999;
        width: 70px;
        flex-shrink: 0;
      }
      .val {
        color: #333;
        flex: 1;
      }
      .phone-icon {
        font-size: 16px;
        padding: 0 8px;
      }
    }
  }
  
  .footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #f9f9f9;
    padding-top: 12px;
    
    .price {
      font-size: 14px;
      font-weight: bold;
      color: #FF9F43;
    }
    
    .actions {
      display: flex;
      gap: 8px;
    }
  }
}
</style>
