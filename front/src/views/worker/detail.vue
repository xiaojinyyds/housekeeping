<script setup lang="ts">
import { showToast } from 'vant'
import { useRoute, useRouter } from 'vue-router'
import apiWorker from '@/api/modules/worker'

definePage({
  name: 'worker-detail-page',
  meta: {
    title: '阿姨详情',
  },
})

const route = useRoute()
const router = useRouter()
const workerId = route.params.id as string

const loading = ref(true)
const worker = ref<any>(null)

async function fetchDetail() {
  loading.value = true
  try {
    const res: any = await apiWorker.getWorkerDetail(workerId)
    if (res.code === 200) {
      worker.value = res.data
    } else {
      showToast('获取详情失败')
    }
  } catch (error) {
    console.error(error)
    showToast('获取详情失败')
  } finally {
    loading.value = false
  }
}

function handleBook() {
  router.push({
    path: '/order/book',
    query: { workerId: workerId }
  })
}

onMounted(() => {
  fetchDetail()
})
</script>

<template>
  <div class="worker-detail-page">
    <van-nav-bar title="阿姨详情" left-arrow fixed placeholder @click-left="router.back()" />
    
    <div v-if="loading" class="loading-state">
      <van-loading type="spinner" />
    </div>
    
    <template v-else-if="worker">
      <!-- 头部卡片 -->
      <div class="header-card">
        <div class="profile">
          <van-image
            round
            width="80"
            height="80"
            :src="worker.id_card_front"
            class="avatar"
          >
            <template #error>
              <van-image round width="80" height="80" src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg" />
            </template>
          </van-image>
          <div class="info">
            <div class="name">
              {{ worker.real_name }}
              <van-tag type="warning" v-if="worker.is_recommended">金牌推荐</van-tag>
            </div>
            <div class="stats">
              <span>{{ worker.age }}岁</span> | <span>{{ worker.experience_years }}年经验</span> | <span>{{ worker.address || '北京' }}</span>
            </div>
            <div class="rating">
              <van-rate v-model="worker.rating" readonly size="12" color="#FF9F43" allow-half />
              <span class="score">{{ worker.rating }}分</span>
              <span class="orders">已服务 {{ worker.completed_orders }} 单</span>
            </div>
          </div>
        </div>
        
        <div class="tags">
          <van-tag plain type="primary" v-for="skill in worker.skills" :key="skill">{{ skill }}</van-tag>
        </div>
      </div>
      
      <!-- 个人简介 -->
      <div class="section-card">
        <div class="sc-title">个人简介</div>
        <div class="sc-content">{{ worker.introduction || '暂无简介' }}</div>
      </div>
      
      <!-- 服务项目 -->
      <div class="section-card">
        <div class="sc-title">服务项目</div>
        <van-cell-group :border="false">
          <van-cell 
            v-for="service in worker.services" 
            :key="service.id"
            :title="service.name"
            :label="service.description"
          >
            <template #right-icon>
              <span class="price">¥{{ service.price }}/小时</span>
            </template>
          </van-cell>
        </van-cell-group>
      </div>
      
      <!-- 用户评价 (暂未实现列表接口，仅占位) -->
      <div class="section-card">
        <div class="sc-title">用户评价</div>
        <van-empty description="暂无评价" image="search" />
      </div>
      
      <div class="bottom-action">
        <van-button 
          round 
          block 
          color="#FF9F43" 
          @click="handleBook"
        >
          立即预约
        </van-button>
      </div>
    </template>
    
    <van-empty v-else description="未找到阿姨信息" />
  </div>
</template>

<style scoped lang="scss">
.worker-detail-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 80px;
}

.loading-state {
  padding: 40px;
  display: flex;
  justify-content: center;
}

.header-card {
  background: #fff;
  padding: 20px 16px;
  margin-bottom: 12px;
  
  .profile {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
    
    .info {
      flex: 1;
      
      .name {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
      }
      
      .stats {
        font-size: 13px;
        color: #666;
        margin-bottom: 8px;
        
        span {
          margin: 0 4px;
          &:first-child { margin-left: 0; }
        }
      }
      
      .rating {
        display: flex;
        align-items: center;
        gap: 6px;
        
        .score {
          color: #FF9F43;
          font-weight: bold;
        }
        
        .orders {
          color: #999;
          font-size: 12px;
          margin-left: 8px;
        }
      }
    }
  }
  
  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}

.section-card {
  background: #fff;
  margin-bottom: 12px;
  padding: 16px;
  
  .sc-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 12px;
    border-left: 3px solid #FF9F43;
    padding-left: 8px;
  }
  
  .sc-content {
    font-size: 14px;
    color: #333;
    line-height: 1.6;
    white-space: pre-wrap;
  }
  
  .price {
    color: #FF4444;
    font-weight: bold;
    font-size: 16px;
  }
}

.bottom-action {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
  padding-bottom: calc(12px + env(safe-area-inset-bottom));
}
</style>
