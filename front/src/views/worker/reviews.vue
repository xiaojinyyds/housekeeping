<script setup lang="ts">
import { showToast } from 'vant'
import apiWorker from '@/api/modules/worker'
import { useUserStore } from '@/store/modules/user'

definePage({
  name: 'worker-reviews',
  meta: {
    title: '我的评价',
    auth: true,
  },
})

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const finished = ref(false)
const list = ref<any[]>([])
const page = ref(1)

async function onLoad() {
  if (!userStore.isWorker) {
    showToast('您不是家政阿姨')
    router.back()
    return
  }

  try {
    const res: any = await apiWorker.getWorkerReviews(userStore.userInfo.id, {
      page: page.value,
      page_size: 10
    })

    if (res.code === 200) {
      if (page.value === 1) {
        list.value = res.data.list
      } else {
        list.value.push(...res.data.list)
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
</script>

<template>
  <div class="reviews-page">
    <van-nav-bar title="我的评价" left-arrow fixed placeholder @click-left="router.back()" />

    <van-pull-refresh v-model="loading" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div class="review-list">
          <div v-for="item in list" :key="item.id" class="review-card">
            <div class="header">
              <div class="user-info">
                <van-image
                  round
                  width="36"
                  height="36"
                  :src="item.user_avatar || 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'"
                />
                <span class="username">{{ item.user_name }}</span>
              </div>
              <span class="date">{{ item.created_at?.split('T')[0] }}</span>
            </div>
            
            <div class="rating">
              <van-rate :model-value="item.rating" readonly :size="14" color="#ffd21e" />
            </div>

            <div class="content">{{ item.content }}</div>

            <div v-if="item.images && item.images.length" class="images">
              <van-image
                v-for="(img, index) in item.images"
                :key="index"
                width="80"
                height="80"
                radius="4"
                :src="img"
                fit="cover"
              />
            </div>
          </div>
        </div>
        
        <van-empty v-if="!loading && list.length === 0" description="暂无评价" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<style scoped lang="scss">
.reviews-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.review-list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.review-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;

      .username {
        font-size: 14px;
        font-weight: bold;
        color: #333;
      }
    }

    .date {
      font-size: 12px;
      color: #999;
    }
  }

  .rating {
    margin-bottom: 8px;
  }

  .content {
    font-size: 14px;
    color: #333;
    line-height: 1.5;
    margin-bottom: 8px;
  }

  .images {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
}
</style>
