<script setup lang="ts">
import { showToast, showLoadingToast, closeToast } from 'vant'
import apiWorker from '@/api/modules/worker'

definePage({
  name: 'worker-schedule',
  meta: {
    title: '时间管理',
  },
})

const router = useRouter()

const loading = ref(true)
const saving = ref(false)
const timeSlots = ref<any[]>([])
const schedule = ref<Record<number, any[]>>({})

// 星期名称
const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
const activeDayIndex = ref(1) // 默认选中周一

// 获取数据
async function fetchData() {
  loading.value = true
  try {
    const res: any = await apiWorker.getMySchedule()
    if (res.code === 200) {
      timeSlots.value = res.data.time_slots || []
      schedule.value = res.data.schedule || {}
    }
  }
  catch (error: any) {
    console.error('获取时间段失败:', error)
    if (error.response?.status === 403) {
      showToast('您不是家政阿姨')
      router.back()
    }
  }
  finally {
    loading.value = false
  }
}

// 切换时间段状态
function toggleSlot(dayIndex: number, slotId: string) {
  const daySlots = schedule.value[dayIndex]
  if (!daySlots)
    return
  const slot = daySlots.find(s => s.time_slot_id === slotId)
  if (slot) {
    slot.is_available = !slot.is_available
  }
}

// 全选当天
function selectAllDay(dayIndex: number) {
  const daySlots = schedule.value[dayIndex]
  if (!daySlots)
    return
  daySlots.forEach((slot) => {
    slot.is_available = true
  })
}

// 清空当天
function clearDay(dayIndex: number) {
  const daySlots = schedule.value[dayIndex]
  if (!daySlots)
    return
  daySlots.forEach((slot) => {
    slot.is_available = false
  })
}

// 复制到其他天
function copyToAll() {
  const sourceSlots = schedule.value[activeDayIndex.value]
  if (!sourceSlots)
    return
  for (let i = 0; i < 7; i++) {
    if (i !== activeDayIndex.value && schedule.value[i]) {
      schedule.value[i].forEach((slot, index) => {
        slot.is_available = sourceSlots[index]?.is_available || false
      })
    }
  }
  showToast('已复制到全部')
}

// 保存
async function saveSchedule() {
  saving.value = true
  showLoadingToast({ message: '保存中...', forbidClick: true })

  try {
    // 收集所有时间段
    const slots: Array<{ day_of_week: number, time_slot_id: string, is_available: boolean }> = []
    for (let day = 0; day < 7; day++) {
      const daySlots = schedule.value[day]
      if (daySlots) {
        daySlots.forEach((slot) => {
          slots.push({
            day_of_week: day,
            time_slot_id: slot.time_slot_id,
            is_available: slot.is_available,
          })
        })
      }
    }

    const res: any = await apiWorker.updateMySchedule({ slots })
    closeToast()

    if (res.code === 200) {
      showToast('保存成功')
    }
    else {
      showToast(res.message || '保存失败')
    }
  }
  catch (error) {
    closeToast()
    showToast('保存失败')
  }
  finally {
    saving.value = false
  }
}

// 获取当天选中数量
function getSelectedCount(dayIndex: number) {
  const daySlots = schedule.value[dayIndex]
  if (!daySlots)
    return 0
  return daySlots.filter(s => s.is_available).length
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="schedule-page">
    <!-- 顶部导航 -->
    <van-nav-bar
      title="时间管理"
      left-arrow
      @click-left="router.back()"
    />

    <van-loading v-if="loading" class="page-loading" />

    <template v-else>
      <!-- 星期选择 -->
      <div class="day-tabs">
        <div
          v-for="(name, index) in dayNames"
          :key="index"
          class="day-tab"
          :class="{ active: activeDayIndex === index }"
          @click="activeDayIndex = index"
        >
          <span class="day-name">{{ name }}</span>
          <span class="count">{{ getSelectedCount(index) }}个</span>
        </div>
      </div>

      <!-- 快捷操作 -->
      <div class="quick-actions">
        <van-button size="small" plain @click="selectAllDay(activeDayIndex)">
          全选
        </van-button>
        <van-button size="small" plain @click="clearDay(activeDayIndex)">
          清空
        </van-button>
        <van-button size="small" plain @click="copyToAll">
          复制到全部
        </van-button>
      </div>

      <!-- 时间段选择 -->
      <div class="slots-section">
        <div class="section-title">
          {{ dayNames[activeDayIndex] }}可预约时间
        </div>
        <div class="slots-grid">
          <div
            v-for="slot in schedule[activeDayIndex]"
            :key="slot.time_slot_id"
            class="slot-item"
            :class="{ selected: slot.is_available }"
            @click="toggleSlot(activeDayIndex, slot.time_slot_id)"
          >
            <div class="slot-name">
              {{ slot.name }}
            </div>
            <div class="slot-time">
              {{ slot.start_time }} - {{ slot.end_time }}
            </div>
            <van-icon
              v-if="slot.is_available"
              name="success"
              class="check-icon"
            />
          </div>
        </div>
      </div>

      <!-- 保存按钮 -->
      <div class="save-bar">
        <van-button
          type="primary"
          block
          round
          :loading="saving"
          color="#FF9F43"
          @click="saveSchedule"
        >
          保存设置
        </van-button>
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
.schedule-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 80px;
}

.page-loading {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

.day-tabs {
  display: flex;
  background: #fff;
  padding: 12px;
  gap: 8px;
  overflow-x: auto;

  .day-tab {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px 14px;
    border-radius: 8px;
    background: #f5f5f5;
    cursor: pointer;
    transition: all 0.2s;

    &.active {
      background: #FF9F43;
      color: #fff;

      .count {
        color: rgba(255, 255, 255, 0.8);
      }
    }

    .day-name {
      font-size: 14px;
      font-weight: 500;
    }

    .count {
      font-size: 11px;
      color: #999;
      margin-top: 2px;
    }
  }
}

.quick-actions {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
}

.slots-section {
  margin: 12px 16px;
  background: #fff;
  border-radius: 12px;
  padding: 16px;

  .section-title {
    font-size: 16px;
    font-weight: bold;
    color: #333;
    margin-bottom: 16px;
  }

  .slots-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;

    .slot-item {
      position: relative;
      padding: 16px;
      border: 2px solid #e0e0e0;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.2s;

      &.selected {
        border-color: #FF9F43;
        background: rgba(255, 159, 67, 0.08);

        .slot-name {
          color: #FF9F43;
        }
      }

      .slot-name {
        font-size: 15px;
        font-weight: 500;
        color: #333;
        margin-bottom: 4px;
      }

      .slot-time {
        font-size: 12px;
        color: #999;
      }

      .check-icon {
        position: absolute;
        top: 8px;
        right: 8px;
        color: #FF9F43;
        font-size: 18px;
      }
    }
  }
}

.save-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px;
  padding-bottom: calc(12px + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}
</style>
