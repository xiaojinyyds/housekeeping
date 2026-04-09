<script setup lang="ts">
import { showToast, showLoadingToast, closeToast } from 'vant'
import { useRoute, useRouter } from 'vue-router'
import apiAppointment from '@/api/modules/appointment'

definePage({
  name: 'order-review',
  meta: {
    title: '评价订单',
    auth: true,
  },
})

const route = useRoute()
const router = useRouter()
const orderId = route.params.id as string

const loading = ref(true)
const order = ref<any>(null)

const form = reactive({
  rating: 5,
  content: '',
  is_anonymous: false
})

const fileList = ref<any[]>([])

async function fetchOrderDetail() {
  try {
    const res: any = await apiAppointment.getAppointmentDetail(orderId)
    if (res.code === 200) {
      order.value = res.data
    } else {
      showToast('获取订单失败')
    }
  } catch (error) {
    showToast('获取订单失败')
  } finally {
    loading.value = false
  }
}

async function submitReview() {
  if (!form.content.trim()) {
    showToast('请输入评价内容')
    return
  }
  
  showLoadingToast({ message: '提交中...', forbidClick: true })
  
  try {
    // 处理图片上传结果 (Mock logic: assuming uploader returns URLs or we upload separately)
    // 真实场景：需要在 uploader after-read 自动上传，或者统一上传。
    // 这里简化：假设 fileList 里的 content 就是 base64 (小图) 或者 只是演示提交
    // apiAppointment.createReview expects string URLs.
    // For demo, we just pass empty list or mock URLs if implemented.
    // 这里暂时忽略图片上传的真实后端交互，只处理逻辑
    const images: string[] = [] 
    
    await apiAppointment.createReview(orderId, {
      ...form,
      images,
      tags: [] 
    })
    
    closeToast()
    showToast('评价成功')
    router.replace('/order/list')
  } catch (error: any) {
    closeToast()
    showToast(error.message || '评价失败')
  }
}

onMounted(() => {
  fetchOrderDetail()
})
</script>

<template>
  <div class="review-page">
    <van-nav-bar title="评价订单" left-arrow fixed placeholder @click-left="router.back()" />
    
    <div v-if="order" class="content">
      <!-- 阿姨信息 -->
      <div class="worker-card">
        <van-image
          width="50"
          height="50"
          round
          src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
        />
        <div class="info">
          <div class="name">{{ order.worker_name }}</div>
          <div class="service">{{ order.service_name }}</div>
        </div>
      </div>
      
      <!-- 评分 -->
      <div class="rating-section">
        <div class="label">服务评分</div>
        <van-rate v-model="form.rating" :size="32" color="#FF9F43" void-icon="star" void-color="#eee" />
        <div class="score-text">{{ form.rating }}分</div>
      </div>
      
      <!-- 内容 -->
      <div class="input-section">
        <van-field
          v-model="form.content"
          type="textarea"
          rows="4"
          placeholder="阿姨服务怎么样？主要做了哪些工作？"
          maxlength="200"
          show-word-limit
          class="comment-input"
        />
        
        <div class="upload-area">
          <van-uploader v-model="fileList" multiple max-count="3" />
        </div>
      </div>
      
      <!-- 匿名 -->
      <div class="anonymous-section">
        <van-checkbox v-model="form.is_anonymous" checked-color="#FF9F43">匿名评价</van-checkbox>
      </div>
      
      <div class="submit-btn">
        <van-button block round color="#FF9F43" @click="submitReview">提交评价</van-button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.review-page {
  min-height: 100vh;
  background: #fff;
  
  .content {
    padding: 16px;
  }
  
  .worker-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 20px;
    border-bottom: 1px solid #f9f9f9;
    
    .info {
      .name {
        font-weight: bold;
        font-size: 16px;
      }
      .service {
        font-size: 13px;
        color: #999;
        margin-top: 4px;
      }
    }
  }
  
  .rating-section {
    padding: 24px 0;
    text-align: center;
    
    .label {
      font-weight: bold;
      margin-bottom: 12px;
      font-size: 16px;
    }
    
    .score-text {
      color: #FF9F43;
      margin-top: 8px;
    }
  }
  
  .input-section {
    background: #f7f8fa;
    border-radius: 8px;
    padding: 12px;
    
    .comment-input {
      background: transparent;
      padding: 0;
    }
    
    .upload-area {
      margin-top: 12px;
    }
  }
  
  .anonymous-section {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }
  
  .submit-btn {
    margin-top: 40px;
  }
}
</style>
