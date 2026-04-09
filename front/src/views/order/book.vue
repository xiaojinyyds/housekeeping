<script setup lang="ts">
import { showToast, showLoadingToast, closeToast } from 'vant'
import { useRoute, useRouter } from 'vue-router'
import apiWorker from '@/api/modules/worker'
import apiAppointment from '@/api/modules/appointment'

definePage({
  name: 'order-book',
  meta: {
    title: '预约服务',
    auth: true,
  },
})

const route = useRoute()
const router = useRouter()
const workerId = route.query.workerId as string

const worker = ref<any>(null)
const services = ref<any[]>([])
const timeSlots = ref<any[]>([])
const availability = ref<any>({})

// 表单数据
const form = reactive({
  service_id: '',
  service_name: '',
  appointment_date: '', // YYYY-MM-DD
  time_slot_id: '',
  time_slot_name: '',
  duration_hours: 2,
  unit_price: 0,
  address: '',
  contact_name: '',
  contact_phone: '',
  remark: ''
})

// UI状态
const showCalendar = ref(false)
const showTimeSlot = ref(false)
const showServicePicker = ref(false)

// 计算属性
const totalPrice = computed(() => {
  return form.unit_price * form.duration_hours
})

const currentService = computed(() => {
  return services.value.find(s => s.id === form.service_id)
})

// 获取阿姨详情和服务
async function fetchWorkerData() {
  if (!workerId) {
    showToast('参数错误')
    router.back()
    return
  }
  
  try {
    const res: any = await apiWorker.getWorkerDetail(workerId)
    if (res.code === 200) {
      worker.value = res.data
      services.value = res.data.services || []
      
      // 默认选中第一个服务
      if (services.value.length > 0) {
        selectService(services.value[0])
      }
    }
  } catch (error) {
    console.error(error)
  }
}

// 获取排班表
async function fetchSchedule() {
  try {
    const res: any = await apiWorker.getWorkerSchedule(workerId)
    if (res.code === 200) {
      timeSlots.value = res.data.time_slots
      availability.value = res.data.availability
    }
  } catch (error) {
    console.error(error)
  }
}

// 选择服务
function selectService(service: any) {
  form.service_id = service.id
  form.service_name = service.name
  form.unit_price = service.price
  showServicePicker.value = false
}

// 日期格式化
function formatDate(date: Date) {
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

// 选择日期确认
function onConfirmDate(value: Date) {
  form.appointment_date = formatDate(value)
  showCalendar.value = false
  // 重置时间段
  form.time_slot_id = ''
  form.time_slot_name = ''
}

// 判断时间段是否可用
function isSlotAvailable(slotId: string) {
  if (!form.appointment_date) return false
  const date = new Date(form.appointment_date)
  const dayOfWeek = date.getDay() // 0-6
  
  const availableSlots = availability.value[dayOfWeek] || availability.value[dayOfWeek.toString()]
  return availableSlots && availableSlots.includes(slotId)
}

// 选择时间段
function selectTimeSlot(slot: any) {
  if (!isSlotAvailable(slot.id)) {
    showToast('该时间段阿姨不可预约')
    return
  }
  form.time_slot_id = slot.id
  form.time_slot_name = slot.name
  showTimeSlot.value = false
}

// 提交订单
async function submitOrder() {
  if (!form.service_id) return showToast('请选择服务项目')
  if (!form.appointment_date) return showToast('请选择预约日期')
  if (!form.time_slot_id) return showToast('请选择服务时间')
  if (!form.contact_name) return showToast('请输入联系人')
  if (!form.contact_phone) return showToast('请输入联系电话')
  if (!form.address) return showToast('请输入服务地址')
  
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    const res: any = await apiAppointment.createAppointment({
      worker_id: workerId,
      ...form
    })
    
    closeToast()
    
    if (res.code === 200) {
      showToast('预约成功')
      router.replace('/order/list')
    } else {
      showToast(res.message || '预约失败')
    }
  } catch (error) {
    closeToast()
    console.error(error)
    showToast('系统繁忙，请稍后重试')
  }
}

onMounted(() => {
  fetchWorkerData()
  fetchSchedule()
})
</script>

<template>
  <div class="book-page">
    <van-nav-bar title="预约服务" left-arrow @click-left="router.back()" />
    
    <div class="content">
      <!-- 阿姨信息 -->
      <div class="worker-card" v-if="worker">
          <van-image
            round
            width="60"
            height="60"
            fit="cover"
            :src="worker.id_card_front"
          >
            <template #error>
              <van-image round width="60" height="60" src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg" />
            </template>
          </van-image>
        <!-- 暂时使用默认头像，因为后端没返回头像URL给前端直接用（在detail里有user_id可以用） -->
        <div class="info">
          <div class="name">{{ worker.real_name }} <span class="tag">金牌阿姨</span></div>
          <div class="desc">工龄{{ worker.experience_years }}年 | 好评率{{ worker.rating }}</div>
        </div>
      </div>
      
      <!-- 服务选择 -->
      <van-cell-group inset title="服务项目">
        <van-cell 
          :title="form.service_name || '请选择服务'" 
          :label="form.unit_price ? `¥${form.unit_price}/小时` : ''"
          is-link 
          @click="showServicePicker = true" 
        />
        <van-cell title="由于目前是标准服务，默认时长2小时">
           <template #right-icon>
             <van-stepper v-model="form.duration_hours" min="2" max="8" />
           </template>
        </van-cell>
      </van-cell-group>
      
      <!-- 时间选择 -->
      <van-cell-group inset title="服务时间">
        <van-cell title="预约日期" :value="form.appointment_date || '请选择日期'" is-link @click="showCalendar = true" />
        <van-cell title="服务时段" :value="form.time_slot_name || '请选择时段'" is-link @click="showTimeSlot = true" />
      </van-cell-group>
      
      <!-- 地址信息 -->
      <van-cell-group inset title="服务信息">
        <van-field v-model="form.contact_name" label="联系人" placeholder="请输入姓名" />
        <van-field v-model="form.contact_phone" label="电话" type="tel" placeholder="请输入手机号" />
        <van-field v-model="form.address" label="地址" placeholder="请输入详细地址（街道/门牌号）" />
        <van-field v-model="form.remark" label="备注" type="textarea" rows="2" placeholder="如有特殊要求请备注" />
      </van-cell-group>
    </div>
    
    <!-- 底部栏 -->
    <van-submit-bar 
      :price="totalPrice * 100" 
      button-text="立即预约" 
      @submit="submitOrder" 
      label="预计金额"
      class="submit-bar"
    >
      <template #button>
        <van-button 
            round 
            type="primary" 
            color="#FF9F43" 
            @click="submitOrder"
            class="submit-btn"
        >
            立即预约
        </van-button>
      </template>
    </van-submit-bar>
    
    <!-- 日期弹窗 -->
    <van-calendar v-model:show="showCalendar" @confirm="onConfirmDate" color="#FF9F43" :min-date="new Date()" />
    
    <!-- 服务选择弹窗 -->
    <van-action-sheet v-model:show="showServicePicker" title="选择服务">
      <div class="service-list">
        <div 
          v-for="item in services" 
          :key="item.id" 
          class="service-item"
          :class="{ active: form.service_id === item.id }"
          @click="selectService(item)"
        >
          <div class="name">{{ item.name }}</div>
          <div class="price">¥{{ item.price }}/小时</div>
          <van-icon name="success" v-if="form.service_id === item.id" color="#FF9F43" />
        </div>
      </div>
    </van-action-sheet>
    
    <!-- 时间段弹窗 -->
    <van-popup v-model:show="showTimeSlot" position="bottom" round>
      <div class="slot-picker">
        <div class="header">选择服务时段</div>
        <div class="slots-grid">
          <div 
            v-for="slot in timeSlots" 
            :key="slot.id"
            class="slot-item"
            :class="{ 
              active: form.time_slot_id === slot.id,
              disabled: !isSlotAvailable(slot.id)
            }"
            @click="selectTimeSlot(slot)"
          >
            {{ slot.name }}
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped lang="scss">
.book-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 60px;
  
  .content {
    padding-top: 12px;
  }
  
  .worker-card {
    background: #fff;
    margin: 0 16px 12px;
    padding: 16px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
    
    .info {
      .name {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 4px;
        
        .tag {
          font-size: 12px;
          background: #FFF0E6;
          color: #FF9F43;
          padding: 2px 6px;
          border-radius: 4px;
          font-weight: normal;
          margin-left: 4px;
        }
      }
      .desc {
        font-size: 13px;
        color: #666;
      }
    }
  }
  
  .service-list {
    padding: 16px;
    
    .service-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px;
      border-bottom: 1px solid #f5f5f5;
      
      &.active {
        color: #FF9F43;
        font-weight: bold;
      }
    }
  }
  
  .slot-picker {
    padding: 16px;
    
    .header {
      text-align: center;
      font-weight: bold;
      font-size: 16px;
      margin-bottom: 16px;
    }
    
    .slots-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      
      .slot-item {
        background: #f5f5f5;
        padding: 12px;
        text-align: center;
        border-radius: 8px;
        font-size: 14px;
        border: 1px solid transparent;
        
        &.active {
          background: #FFF0E6;
          border-color: #FF9F43;
          color: #FF9F43;
        }
        
        &.disabled {
          color: #ccc;
          background: #f9f9f9;
          text-decoration: line-through;
        }
      }
    }
  }
}
  .submit-bar {
    border-top: 1px solid #f5f5f5;
  }
  
  .submit-btn {
    width: 120px;
    height: 40px;
  }
</style>
