<script setup lang="ts">
import { showToast } from 'vant'
import { areaList } from '@vant/area-data'
import apiWorker from '@/api/modules/worker'
import apiAnnouncement from '@/api/modules/announcement'

definePage({
  name: 'index',
  meta: {
    title: '首页',
  },
})

const router = useRouter()
const userStore = useUserStore()

const active = ref(0)
const loading = ref(false)
const workerList = ref<any[]>([])

// 公告相关
const announcementList = ref<any[]>([])
const currentCity = ref('全国')
const currentArea = ref('') // 当前选择的完整路径（省/市/区）
const currentDisplayName = ref('全国') // 显示用的名称
const showCityPicker = ref(false)

// 构建省市区数据
const provinceList = computed(() => {
  return Object.entries(areaList.province_list).map(([code, name]) => ({
    code,
    name: name as string
  }))
})

const cityList = computed(() => {
  if (!selectedProvince.value) return []
  const provinceCode = selectedProvince.value.code.substring(0, 2)
  return Object.entries(areaList.city_list)
    .filter(([code]) => code.startsWith(provinceCode))
    .map(([code, name]) => ({ code, name: name as string }))
})

const districtList = computed(() => {
  if (!selectedCity.value) return []
  const cityCode = selectedCity.value.code.substring(0, 4)
  return Object.entries(areaList.county_list)
    .filter(([code]) => code.startsWith(cityCode))
    .map(([code, name]) => ({ code, name: name as string }))
})

// 选中的省市区
const selectedProvince = ref<{ code: string; name: string } | null>(null)
const selectedCity = ref<{ code: string; name: string } | null>(null)
const selectedDistrict = ref<{ code: string; name: string } | null>(null)

// 选择省
function selectProvince(province: { code: string; name: string }) {
  selectedProvince.value = province
  selectedCity.value = null
  selectedDistrict.value = null
}

// 选择市
function selectCity(city: { code: string; name: string }) {
  selectedCity.value = city
  selectedDistrict.value = null
}

// 选择区
function selectDistrict(district: { code: string; name: string }) {
  selectedDistrict.value = district
}

// 确认选择
function confirmCitySelection() {
  if (!selectedProvince.value) {
    // 没选任何，清空筛选
    currentArea.value = ''
    currentCity.value = '全国'
    currentDisplayName.value = '全国'
  } else if (!selectedCity.value) {
    // 只选了省
    currentArea.value = selectedProvince.value.name
    currentCity.value = selectedProvince.value.name
    currentDisplayName.value = selectedProvince.value.name
  } else if (!selectedDistrict.value) {
    // 选了省和市
    currentArea.value = `${selectedProvince.value.name}/${selectedCity.value.name}`
    currentCity.value = selectedCity.value.name
    currentDisplayName.value = selectedCity.value.name
  } else {
    // 选了省市区
    currentArea.value = `${selectedProvince.value.name}/${selectedCity.value.name}/${selectedDistrict.value.name}`
    currentCity.value = selectedDistrict.value.name
    currentDisplayName.value = selectedDistrict.value.name
  }
  
  // 保存到本地
  localStorage.setItem('currentCity', currentCity.value)
  localStorage.setItem('currentArea', currentArea.value)
  
  showCityPicker.value = false
  getRecommendWorkers()
}

// 重置选择
function resetCitySelection() {
  selectedProvince.value = null
  selectedCity.value = null
  selectedDistrict.value = null
}

// 打开城市选择器
function changeCity() {
  // 重置选择状态
  resetCitySelection()
  showCityPicker.value = true
}

// 轮播图数据
const banners = [
  {
    id: 1,
    imgUrl: new URL('@/assets/images/轮播图1.png', import.meta.url).href,
    title: '新客首单立减',
    subTitle: '专业保洁 ¥35/小时起',
    buttonText: '立即预约',
  },
  {
    id: 2,
    imgUrl: new URL('@/assets/images/轮播图2.png', import.meta.url).href,
    title: '品质月嫂服务',
    subTitle: '持证上岗 经验丰富',
    buttonText: '查看详情',
  },
  {
    id: 3,
    imgUrl: new URL('@/assets/images/轮播图3.png', import.meta.url).href,
    title: '春节大扫除',
    subTitle: '全屋深度清洁 8折优惠',
    buttonText: '立即抢购',
  },
  {
    id: 4,
    imgUrl: new URL('@/assets/images/轮播图4.png', import.meta.url).href,
    title: '专业育儿嫂',
    subTitle: '科学育儿 贴心照护',
    buttonText: '了解更多',
  },
  {
    id: 5,
    imgUrl: new URL('@/assets/images/轮播图5.png', import.meta.url).href,
    title: '家电维修服务',
    subTitle: '快速上门 专业维修',
    buttonText: '立即预约',
  },
]

// 服务分类 - 使用Vant图标
const categories = [
  { icon: 'brush-o', name: '保洁', color: '#FF9F43' },
  { icon: 'smile-o', name: '月嫂', color: '#FF7F50' },
  { icon: 'friends-o', name: '育儿', color: '#FFB84D' },
  { icon: 'like-o', name: '护理', color: '#FFA07A' },
  { icon: 'fire-o', name: '烹饪', color: '#FFAD60' },
  { icon: 'user-o', name: '陪护', color: '#FF8C69' },
  { icon: 'setting-o', name: '维修', color: '#FFC078' },
  { icon: 'bag-o', name: '洗衣', color: '#FFD700' },
]

// 搜索
function onSearch() {
  showToast('搜索功能开发中')
}

// 轮播图点击
function onBannerClick(banner: any) {
  // 根据不同的 banner 跳转不同的页面
  if (banner.title.includes('家电')) {
    goWorkerList('维修')
  } else if (banner.title.includes('月嫂')) {
     goWorkerList('月嫂')
  } else {
    goWorkerList()
  }
}

// 获取推荐家政阿姨
async function getRecommendWorkers() {
  loading.value = true
  try {
    const res: any = await apiWorker.getWorkers({
      page: 1,
      page_size: 6,
      is_available: true,
      is_recommended: true, // 只获取推荐的阿姨
      city: currentArea.value || undefined, // 传递城市筛选参数
    })
    if (res.code === 200) {
      workerList.value = res.data.list || []
    }
  }
  catch (error: any) {
    console.error('获取家政阿姨列表失败:', error)
  }
  finally {
    loading.value = false
  }
}

// 跳转到家政阿姨列表
function goWorkerList(skill?: string) {
  router.push({
    path: '/worker/list',
    query: skill ? { skill, city: currentArea.value || currentCity.value } : { city: currentArea.value || currentCity.value },
  })
}

// 跳转到家政阿姨详情
function goWorkerDetail(id: string) {
  router.push(`/worker/detail/${id}`)
}

// 预约阿姨
function bookWorker(worker: any, event: Event) {
  event.stopPropagation()
  if (!userStore.isLogin) {
    showToast('请先登录')
    router.push('/login')
    return
  }
  router.push({
    path: '/order/book',
    query: { workerId: worker.user_id }
  })
}

// 获取公告列表
async function getAnnouncements() {
  try {
    const res: any = await apiAnnouncement.getList({ page: 1, page_size: 5 })
    if (res.code === 200) {
      announcementList.value = res.data.list || []
    }
  } catch (error) {
    console.error('获取公告失败:', error)
  }
}

// 跳转公告详情
function goAnnouncementDetail(id: string) {
  router.push(`/announcement/${id}`)
}

onMounted(() => {
  // 读取本地存储的城市
  const savedCity = localStorage.getItem('currentCity')
  const savedArea = localStorage.getItem('currentArea')
  if (savedCity) {
    currentCity.value = savedCity
  }
  if (savedArea) {
    currentArea.value = savedArea
  }
  
  getRecommendWorkers()
  getAnnouncements()
})
</script>

<template>
  <div class="home-page">
    <!-- 沉浸式头部 -->
    <div class="header-section">
      <div class="header-top">
        <!-- 左侧定位 -->
        <div class="location" @click="changeCity">
          <van-icon name="location-o" />
          <span>{{ currentCity }}</span>
          <van-icon name="arrow-down" size="12" />
        </div>

        <!-- 右侧搜索框 -->
        <div class="search-wrapper">
          <van-search
            placeholder="搜索保洁/月嫂/维修"
            background="transparent"
            shape="round"
            @click="onSearch"
          />
        </div>
      </div>
    </div>

    <!-- 轮播图 -->
    <div class="banner-section">
      <van-swipe :autoplay="3000" indicator-color="#FF9F43" class="banner-swipe">
        <van-swipe-item v-for="banner in banners" :key="banner.id">
          <div class="banner-content" :style="{ backgroundImage: `url(${banner.imgUrl})` }">
            <!-- 渐变遮罩 -->
            <div class="banner-overlay" />
            
            <!-- 营销文案 -->
            <div class="banner-text">
              <h3 class="banner-title">{{ banner.title }}</h3>
              <p class="banner-subtitle">{{ banner.subTitle }}</p>
              <van-button
                round
                size="small"
                color="#FF9F43"
                class="banner-button"
                @click="onBannerClick(banner)"
              >
                {{ banner.buttonText }}
              </van-button>
            </div>
          </div>
        </van-swipe-item>
      </van-swipe>
    </div>

    <!-- 公告通知栏 -->
    <div v-if="announcementList.length > 0" class="notice-section">
      <div class="notice-icon">
        <van-icon name="volume-o" color="#FF9F43" size="18" />
      </div>
      <van-swipe
        class="notice-swipe"
        vertical
        :autoplay="3000"
        :touchable="false"
        :show-indicators="false"
      >
        <van-swipe-item
          v-for="item in announcementList"
          :key="item.id"
          @click="goAnnouncementDetail(item.id)"
        >
          <div class="notice-content">
            <van-tag v-if="item.is_top" type="danger" class="top-tag">置顶</van-tag>
            <span class="notice-title">{{ item.title }}</span>
          </div>
        </van-swipe-item>
      </van-swipe>
      <van-icon name="arrow" color="#999" size="14" class="notice-arrow" />
    </div>

    <!-- 服务分类（金刚区） -->
    <div class="category-section">
      <van-grid :border="false" :column-num="4" :gutter="0">
        <van-grid-item
          v-for="item in categories"
          :key="item.name"
          @click="goWorkerList(item.name)"
        >
          <template #icon>
            <div class="category-icon" :style="{ color: item.color }">
              <van-icon :name="item.icon" size="32" />
            </div>
          </template>
          <template #text>
            <span class="category-text">{{ item.name }}</span>
          </template>
        </van-grid-item>
      </van-grid>
    </div>

    <!-- 推荐金牌阿姨 -->
    <div class="recommend-section">
      <div class="section-header">
        <h2 class="section-title">推荐金牌阿姨</h2>
        <div class="more-link" @click="goWorkerList()">
          <span>查看全部</span>
          <van-icon name="arrow" size="14" />
        </div>
      </div>

      <van-loading v-if="loading" class="loading" />

      <div v-else-if="workerList.length > 0" class="auntie-list">
        <div
          v-for="worker in workerList"
          :key="worker.id"
          class="auntie-card"
          @click="goWorkerDetail(worker.user_id)"
        >
          <div class="card-left">
            <van-image
              round
              width="60"
              height="60"
              :src="worker.id_card_front"
              fit="cover"
              class="auntie-avatar"
            >
              <template #error>
                <div class="avatar-placeholder">
                  <van-icon name="user-o" size="30" color="#ccc" />
                </div>
              </template>
            </van-image>
          </div>

          <div class="card-middle">
            <div class="auntie-name">
              {{ worker.real_name }}
              <van-tag
                v-if="worker.is_available"
                type="success"
              >
                可接单
              </van-tag>
            </div>
            <div class="auntie-info">
              <van-tag plain v-if="worker.skills && worker.skills.length > 0">
                {{ worker.skills[0] }}
              </van-tag>
            </div>
            <div class="auntie-rating">
              <van-rate
                :model-value="worker.rating || 5"
                :size="14"
                color="#FF9F43"
                void-color="#eee"
                readonly
                allow-half
              />
              <span class="rating-text">{{ worker.rating || 5.0 }}</span>
              <span class="orders-text">已服务{{ worker.completed_orders || 0 }}单</span>
            </div>
          </div>

          <div class="card-right">
            <div class="price">
              <span class="price-symbol">¥</span>
              <span class="price-value">{{ worker.hourly_rate || '--' }}</span>
              <span class="price-unit">/时</span>
            </div>
            <van-button
              type="primary"
              size="small"
              round
              color="#FF9F43"
              @click="bookWorker(worker, $event)"
            >
              预约
            </van-button>
          </div>
        </div>
      </div>

      <van-empty v-else description="暂无推荐阿姨" />
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

    <!-- 城市选择弹窗 -->
    <van-popup
      v-model:show="showCityPicker"
      position="bottom"
      round
      :style="{ height: '60%' }"
    >
      <div class="city-picker">
        <div class="picker-header">
          <span class="cancel-btn" @click="showCityPicker = false">取消</span>
          <span class="title">选择服务区域</span>
          <span class="confirm-btn" @click="confirmCitySelection">确定</span>
        </div>
        
        <div class="picker-tip">
          提示：可只选省或市，不必选到区
        </div>
        
        <div class="picker-body">
          <!-- 省份列表 -->
          <div class="picker-column">
            <div class="column-title">省份</div>
            <div class="column-list">
              <div
                v-for="province in provinceList"
                :key="province.code"
                class="column-item"
                :class="{ active: selectedProvince?.code === province.code }"
                @click="selectProvince(province)"
              >
                {{ province.name }}
              </div>
            </div>
          </div>
          
          <!-- 城市列表 -->
          <div class="picker-column">
            <div class="column-title">城市</div>
            <div class="column-list">
              <div
                v-for="city in cityList"
                :key="city.code"
                class="column-item"
                :class="{ active: selectedCity?.code === city.code }"
                @click="selectCity(city)"
              >
                {{ city.name }}
              </div>
              <div v-if="!selectedProvince" class="column-empty">请先选择省份</div>
            </div>
          </div>
          
          <!-- 区县列表 -->
          <div class="picker-column">
            <div class="column-title">区县</div>
            <div class="column-list">
              <div
                v-for="district in districtList"
                :key="district.code"
                class="column-item"
                :class="{ active: selectedDistrict?.code === district.code }"
                @click="selectDistrict(district)"
              >
                {{ district.name }}
              </div>
              <div v-if="!selectedCity" class="column-empty">请先选择城市</div>
            </div>
          </div>
        </div>
        
        <div class="selected-path">
          当前选择：{{ selectedProvince ? (selectedProvince.name + (selectedCity ? '/' + selectedCity.name : '') + (selectedDistrict ? '/' + selectedDistrict.name : '')) : '全国' }}
          <span v-if="selectedProvince" class="clear-btn" @click="resetCitySelection">清除</span>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped lang="scss">
.home-page {
  min-height: 100vh;
  background: #F7F8FA;
  padding-bottom: 60px;
}

// 沉浸式头部
.header-section {
  background: linear-gradient(to right, #FF9F43, #FF7F50);
  padding: 12px 16px 16px;
  padding-top: calc(12px + env(safe-area-inset-top));

  .header-top {
    display: flex;
    align-items: center;
    gap: 12px;

    .location {
      display: flex;
      align-items: center;
      gap: 4px;
      color: #fff;
      font-size: 15px;
      font-weight: 500;
      cursor: pointer;
      flex-shrink: 0;

      .van-icon {
        font-size: 16px;
      }
    }

    .search-wrapper {
      flex: 1;

      :deep(.van-search) {
        padding: 0;

        .van-search__content {
          background: #fff;
          border-radius: 20px;
          padding-left: 16px;
        }

        .van-field__control {
          font-size: 14px;
          color: #333;

          &::placeholder {
            color: #999;
          }
        }
      }
    }
  }
}

// 轮播图
.banner-section {
  margin: 10px 16px;

  .banner-swipe {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(255, 127, 80, 0.15);

    .banner-content {
      position: relative;
      width: 100%;
      height: 160px;
      background-size: cover;
      background-position: center;
      background-repeat: no-repeat;
      display: flex;
      align-items: center;

      // 渐变遮罩层
      .banner-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(to right, rgba(0, 0, 0, 0.6) 0%, rgba(0, 0, 0, 0.3) 50%, transparent 100%);
        z-index: 1;
      }

      // 营销文案层
      .banner-text {
        position: relative;
        z-index: 2;
        padding: 0 24px;
        max-width: 70%;

        .banner-title {
          font-size: 22px;
          font-weight: bold;
          color: #fff;
          margin-bottom: 8px;
          text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
          line-height: 1.3;
        }

        .banner-subtitle {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.95);
          margin-bottom: 12px;
          text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
          line-height: 1.4;
        }

        .banner-button {
          height: 32px;
          padding: 0 20px;
          font-size: 13px;
          font-weight: 600;
          box-shadow: 0 4px 12px rgba(255, 159, 67, 0.4);
          border: none;

          &:active {
            transform: scale(0.95);
          }
        }
      }
    }
  }
}

// 公告通知栏
.notice-section {
  display: flex;
  align-items: center;
  margin: 0 16px 12px;
  padding: 10px 12px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

  .notice-icon {
    flex-shrink: 0;
    margin-right: 10px;
  }

  .notice-swipe {
    flex: 1;
    height: 24px;
    overflow: hidden;

    .notice-content {
      display: flex;
      align-items: center;
      height: 24px;
      line-height: 24px;

      .top-tag {
        flex-shrink: 0;
        margin-right: 6px;
        transform: scale(0.85);
      }

      .notice-title {
        flex: 1;
        font-size: 14px;
        color: #333;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }

  .notice-arrow {
    flex-shrink: 0;
    margin-left: 8px;
  }
}

// 服务分类
.category-section {
  background: #fff;
  margin: 12px 16px;
  border-radius: 12px;
  padding: 12px 0;

  :deep(.van-grid-item__content) {
    padding: 12px 8px;
  }

  .category-icon {
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .category-text {
    font-size: 13px;
    color: #333;
    font-weight: 500;
  }
}

// 推荐阿姨
.recommend-section {
  margin: 12px 16px;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;

    .section-title {
      font-size: 18px;
      font-weight: bold;
      color: #333;
    }

    .more-link {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 13px;
      color: #999;
      cursor: pointer;

      &:active {
        opacity: 0.7;
      }
    }
  }

  .loading {
    padding: 40px 0;
  }

  .auntie-list {
    display: flex;
    flex-direction: column;
    gap: 0;

    .auntie-card {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px;
      background: #fff;
      border-bottom: 1px solid #F0F0F0;
      cursor: pointer;
      transition: background 0.2s;

      &:first-child {
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
      }

      &:last-child {
        border-bottom: none;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
      }

      &:active {
        background: #F9F9F9;
      }

      .card-left {
        flex-shrink: 0;

        .auntie-avatar {
          border: 2px solid #FFF5E6;
        }

        .avatar-placeholder {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 30px;
          background: #F7F8FA;
        }
      }

      .card-middle {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 6px;

        .auntie-name {
          font-size: 16px;
          font-weight: bold;
          color: #333;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .auntie-info {
          display: flex;
          gap: 6px;
        }

        .auntie-rating {
          display: flex;
          align-items: center;
          gap: 6px;

          .rating-text {
            font-size: 13px;
            color: #FF9F43;
            font-weight: 600;
          }

          .orders-text {
            font-size: 12px;
            color: #999;
          }
        }
      }

      .card-right {
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 8px;

        .price {
          display: flex;
          align-items: baseline;
          color: #FF9F43;

          .price-symbol {
            font-size: 12px;
            font-weight: 600;
          }

          .price-value {
            font-size: 20px;
            font-weight: bold;
          }

          .price-unit {
            font-size: 12px;
            color: #999;
          }
        }

        .van-button {
          min-width: 60px;
          height: 28px;
          font-size: 13px;
        }
      }
    }
  }
}

// 城市选择器
.city-picker {
  display: flex;
  flex-direction: column;
  height: 100%;
  
  .picker-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid #f5f5f5;
    
    .title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
    }
    
    .cancel-btn {
      font-size: 14px;
      color: #999;
    }
    
    .confirm-btn {
      font-size: 14px;
      color: #FF9F43;
      font-weight: 500;
    }
  }
  
  .picker-tip {
    padding: 8px 16px;
    font-size: 12px;
    color: #FF9F43;
    background: #FFF8F0;
    text-align: center;
  }
  
  .picker-body {
    flex: 1;
    display: flex;
    overflow: hidden;
    
    .picker-column {
      flex: 1;
      display: flex;
      flex-direction: column;
      border-right: 1px solid #f5f5f5;
      
      &:last-child {
        border-right: none;
      }
      
      .column-title {
        padding: 10px;
        font-size: 13px;
        color: #999;
        text-align: center;
        background: #fafafa;
        border-bottom: 1px solid #f5f5f5;
      }
      
      .column-list {
        flex: 1;
        overflow-y: auto;
        
        .column-item {
          padding: 12px 10px;
          font-size: 14px;
          color: #333;
          text-align: center;
          border-bottom: 1px solid #f9f9f9;
          
          &.active {
            color: #FF9F43;
            background: #FFF8F0;
            font-weight: 500;
          }
          
          &:active {
            background: #f5f5f5;
          }
        }
        
        .column-empty {
          padding: 20px;
          font-size: 13px;
          color: #ccc;
          text-align: center;
        }
      }
    }
  }
  
  .selected-path {
    padding: 12px 16px;
    font-size: 13px;
    color: #666;
    background: #fafafa;
    border-top: 1px solid #f5f5f5;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .clear-btn {
      color: #FF9F43;
      font-size: 12px;
    }
  }
}
</style>
