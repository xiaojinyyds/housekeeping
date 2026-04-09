<script setup lang="ts">
import { showToast } from 'vant'
import apiAnnouncement from '@/api/modules/announcement'

definePage({
  name: 'announcement-detail',
  meta: {
    title: '公告详情',
  },
})

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const announcement = ref<any>(null)
const relatedList = ref<any[]>([])
const announcementId = computed(() => {
  const params = route.params as any
  return params.id as string
})

// 默认封面图（家政服务场景）
const defaultCover = new URL('@/assets/images/轮播图1.png', import.meta.url).href

// 类型映射：英文 -> 中文
const typeMap: Record<string, string> = {
  notice: '通知',
  news: '资讯',
  activity: '活动',
  recruit: '招聘',
  announcement: '公告',
}

// 获取中文类型名
function getTypeName(type: string) {
  return typeMap[type] || type || '公告'
}

// 获取公告详情
async function getAnnouncementDetail() {
  loading.value = true
  try {
    const res: any = await apiAnnouncement.getDetail(announcementId.value)
    if (res.code === 200) {
      announcement.value = res.data
      // 获取相关推荐
      getRelatedAnnouncements()
    } else {
      showToast(res.message || '获取公告失败')
    }
  } catch (error: any) {
    showToast(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 获取相关推荐
async function getRelatedAnnouncements() {
  try {
    const res: any = await apiAnnouncement.getList({ page: 1, page_size: 4 })
    if (res.code === 200) {
      // 过滤掉当前公告
      relatedList.value = (res.data.list || [])
        .filter((item: any) => item.id !== announcementId.value)
        .slice(0, 3)
    }
  } catch (error) {
    console.error('获取相关推荐失败:', error)
  }
}

// 格式化日期
function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}年${month}月${day}日`
}

// 跳转到其他公告
function goAnnouncement(id: string) {
  router.push(`/announcement/${id}`)
}

// 联系我们 / 立即报名
function handleAction() {
  // 根据公告类型执行不同操作
  if (announcement.value?.type === 'recruit') {
    // 招聘类公告 -> 跳转到阿姨入驻申请
    router.push('/worker/apply')
  } else {
    // 其他公告 -> 联系客服
    showToast('客服功能开发中')
  }
}

// 返回首页
function goHome() {
  router.push('/')
}

onMounted(() => {
  getAnnouncementDetail()
})

// 监听路由变化，刷新内容
watch(() => announcementId.value, (newId) => {
  if (newId) {
    getAnnouncementDetail()
    // 滚动到顶部
    window.scrollTo(0, 0)
  }
})
</script>

<template>
  <div class="announcement-detail-page">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      title=""
      left-arrow
      fixed
      placeholder
      :border="false"
      class="nav-bar"
      @click-left="router.back()"
    >
      <template #right>
        <van-icon name="wap-home-o" size="22" @click="goHome" />
      </template>
    </van-nav-bar>

    <van-loading v-if="loading" class="loading" />

    <template v-else-if="announcement">
      <!-- Hero 封面图区域 -->
      <div class="hero-section">
        <div class="hero-image">
          <img 
            :src="announcement.cover_image || defaultCover" 
            alt="封面"
            @error="(e: Event) => (e.target as HTMLImageElement).src = defaultCover"
          >
        </div>
        <div class="hero-gradient" />
      </div>

      <!-- 文章主体 -->
      <div class="article-wrapper">
        <!-- 标题与元数据 -->
        <div class="article-header">
          <h1 class="article-title">{{ announcement.title }}</h1>
          <div class="article-meta">
            <div class="meta-left">
              <van-tag v-if="announcement.is_top" type="danger">置顶</van-tag>
              <van-tag type="primary" plain>{{ getTypeName(announcement.type) }}</van-tag>
            </div>
            <div class="meta-right">
              <van-icon name="clock-o" size="12" />
              <span>{{ formatDate(announcement.publish_time || announcement.created_at) }}</span>
            </div>
          </div>
        </div>

        <!-- 正文内容 -->
        <div class="article-content" v-html="announcement.content"></div>

        <!-- 行动按钮 -->
        <div class="action-section">
          <van-button 
            type="primary" 
            block 
            round 
            color="#FF9F43"
            class="action-btn"
            @click="handleAction"
          >
            <van-icon :name="announcement.type === 'recruit' ? 'friends-o' : 'service-o'" />
            <span>{{ announcement.type === 'recruit' ? '立即报名' : '联系我们' }}</span>
          </van-button>
        </div>

        <!-- 分割线 -->
        <van-divider class="section-divider">
          <van-icon name="star-o" color="#FF9F43" />
        </van-divider>

        <!-- 相关推荐 -->
        <div v-if="relatedList.length > 0" class="related-section">
          <div class="section-title">
            <span class="title-text">相关推荐</span>
          </div>
          <div class="related-list">
            <div 
              v-for="item in relatedList" 
              :key="item.id" 
              class="related-item"
              @click="goAnnouncement(item.id)"
            >
              <div class="related-cover">
                <img 
                  :src="item.cover_image || defaultCover" 
                  alt=""
                  @error="(e: Event) => (e.target as HTMLImageElement).src = defaultCover"
                >
              </div>
              <div class="related-info">
                <div class="related-title">{{ item.title }}</div>
                <div class="related-meta">
                  <van-tag type="primary" plain>{{ getTypeName(item.type) }}</van-tag>
                  <span class="related-date">{{ formatDate(item.publish_time) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部留白 -->
        <div class="footer-space" />
      </div>
    </template>

    <van-empty v-else description="公告不存在或已删除" />
  </div>
</template>

<style scoped lang="scss">
.announcement-detail-page {
  min-height: 100vh;
  background: #fff;
}

.nav-bar {
  :deep(.van-nav-bar__content) {
    background: transparent;
  }
  
  :deep(.van-nav-bar__left),
  :deep(.van-nav-bar__right) {
    .van-icon {
      color: #333;
      background: rgba(255, 255, 255, 0.9);
      border-radius: 50%;
      padding: 6px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
  }
}

.loading {
  padding: 100px 0;
}

// Hero 封面图
.hero-section {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;

  .hero-image {
    width: 100%;
    height: 100%;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .hero-gradient {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 80px;
    background: linear-gradient(to bottom, transparent, #fff);
    pointer-events: none;
  }
}

// 文章主体
.article-wrapper {
  position: relative;
  margin-top: -20px;
  padding: 0 20px;
  background: #fff;
  border-radius: 20px 20px 0 0;
}

// 标题与元数据
.article-header {
  padding-top: 24px;
  margin-bottom: 20px;

  .article-title {
    font-size: 22px;
    font-weight: bold;
    color: #333;
    line-height: 1.4;
    margin-bottom: 16px;
  }

  .article-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .meta-left {
      display: flex;
      gap: 8px;

      :deep(.van-tag) {
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 4px;
      }
    }

    .meta-right {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 13px;
      color: #969799;
    }
  }
}

// 正文内容
.article-content {
  font-size: 16px;
  color: #444;
  line-height: 1.8;
  word-break: break-word;
  min-height: 100px;

  :deep(p) {
    margin-bottom: 16px;
  }

  :deep(img) {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin: 16px 0;
    display: block;
  }

  :deep(a) {
    color: #FF9F43;
    text-decoration: none;
  }

  :deep(h1), :deep(h2), :deep(h3) {
    margin: 24px 0 12px;
    color: #333;
    font-weight: 600;
  }

  :deep(ul), :deep(ol) {
    padding-left: 20px;
    margin-bottom: 16px;
  }

  :deep(li) {
    margin-bottom: 8px;
  }

  :deep(blockquote) {
    margin: 16px 0;
    padding: 12px 16px;
    background: #FFF8F0;
    border-left: 4px solid #FF9F43;
    border-radius: 0 8px 8px 0;
    color: #666;
  }
}

// 行动按钮
.action-section {
  margin: 32px 0;

  .action-btn {
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    box-shadow: 0 4px 16px rgba(255, 159, 67, 0.3);

    .van-icon {
      margin-right: 6px;
    }
  }
}

// 分割线
.section-divider {
  margin: 24px 0;
  
  :deep(.van-divider__content) {
    padding: 0 16px;
  }
}

// 相关推荐
.related-section {
  .section-title {
    margin-bottom: 16px;

    .title-text {
      font-size: 18px;
      font-weight: bold;
      color: #333;
      position: relative;
      padding-left: 12px;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 18px;
        background: linear-gradient(to bottom, #FF9F43, #FF7F50);
        border-radius: 2px;
      }
    }
  }

  .related-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .related-item {
    display: flex;
    gap: 12px;
    padding: 12px;
    background: #F7F8FA;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s;

    &:active {
      background: #F0F1F2;
      transform: scale(0.98);
    }

    .related-cover {
      flex-shrink: 0;
      width: 100px;
      height: 70px;
      border-radius: 8px;
      overflow: hidden;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }

    .related-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-width: 0;

      .related-title {
        font-size: 15px;
        font-weight: 500;
        color: #333;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .related-meta {
        display: flex;
        align-items: center;
        gap: 8px;

        :deep(.van-tag) {
          font-size: 11px;
          padding: 1px 6px;
          transform: scale(0.9);
          transform-origin: left center;
        }

        .related-date {
          font-size: 12px;
          color: #969799;
        }
      }
    }
  }
}

// 底部留白
.footer-space {
  height: 40px;
}
</style>
