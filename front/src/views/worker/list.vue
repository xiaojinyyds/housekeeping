<script setup lang="ts">
import { showToast } from 'vant'
import { areaList } from '@vant/area-data'
import apiWorker from '@/api/modules/worker'
import { useUserStore } from '@/store/modules/user'

definePage({
  name: 'worker-list',
  meta: {
    title: '家政阿姨',
  },
})

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const active = ref('/worker/list')

const loading = ref(false)
const finished = ref(false)
const workerList = ref<any[]>([])
const page = ref(1)
const pageSize = 10

// 城市选择
const showCityPicker = ref(false)
const currentCity = ref('全国')
const currentArea = ref('') // 完整路径：省/市/区

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
    currentArea.value = ''
    currentCity.value = '全国'
  } else if (!selectedCity.value) {
    currentArea.value = selectedProvince.value.name
    currentCity.value = selectedProvince.value.name
  } else if (!selectedDistrict.value) {
    currentArea.value = `${selectedProvince.value.name}/${selectedCity.value.name}`
    currentCity.value = selectedCity.value.name
  } else {
    currentArea.value = `${selectedProvince.value.name}/${selectedCity.value.name}/${selectedDistrict.value.name}`
    currentCity.value = selectedDistrict.value.name
  }
  
  localStorage.setItem('currentCity', currentCity.value)
  localStorage.setItem('currentArea', currentArea.value)
  
  showCityPicker.value = false
  getWorkerList(true)
}

// 重置选择
function resetCitySelection() {
  selectedProvince.value = null
  selectedCity.value = null
  selectedDistrict.value = null
}

// 打开城市选择器
function openCityPicker() {
  resetCitySelection()
  showCityPicker.value = true
}

// 筛选条件
const showFilter = ref(false)
const filterSkill = ref(route.query.skill as string || '')
const filterAvailable = ref<boolean | undefined>(undefined)

// 获取家政阿姨列表
async function getWorkerList(isRefresh = false) {
  if (isRefresh) {
    page.value = 1
    workerList.value = []
    finished.value = false
  }

  loading.value = true
  try {
    const res: any = await apiWorker.getWorkers({
      page: page.value,
      page_size: pageSize,
      is_available: filterAvailable.value,
      skills: filterSkill.value || undefined,
      city: currentArea.value || undefined,
    })

    if (res.code === 200) {
      if (isRefresh) {
        workerList.value = res.data.list
      }
      else {
        workerList.value.push(...res.data.list)
      }

      // 判断是否还有更多数据
      if (res.data.list.length < pageSize) {
        finished.value = true
      }
      else {
        page.value++
      }
    }
  }
  catch (error: any) {
    showToast(error.message || '加载失败')
    finished.value = true
  }
  finally {
    loading.value = false
  }
}

// 下拉刷新
async function onRefresh() {
  await getWorkerList(true)
}

// 上拉加载
async function onLoad() {
  await getWorkerList()
}

// 应用筛选
function applyFilter() {
  showFilter.value = false
  getWorkerList(true)
}

// 重置筛选
function resetFilter() {
  filterSkill.value = ''
  filterAvailable.value = undefined
  showFilter.value = false
  getWorkerList(true)
}

// 跳转详情
function goDetail(id: string) {
  router.push(`/worker/detail/${id}`)
}

onMounted(() => {
  // 读取本地存储的城市或从路由参数获取
  const savedCity = localStorage.getItem('currentCity')
  const savedArea = localStorage.getItem('currentArea')
  const routeCity = route.query.city as string
  
  if (routeCity) {
    currentArea.value = routeCity
    // 从路径中提取显示名称
    const parts = routeCity.split('/')
    currentCity.value = parts[parts.length - 1]
  } else if (savedCity && savedArea) {
    currentCity.value = savedCity
    currentArea.value = savedArea
  }
  
  getWorkerList(true)
})
</script>

<template>
  <div class="worker-list-page">
    <van-nav-bar
      title="家政阿姨"
      left-arrow
      @click-left="router.back()"
    >
      <template #left>
        <div class="nav-left" @click.stop="openCityPicker">
          <van-icon name="location-o" />
          <span class="city-name">{{ currentCity }}</span>
          <van-icon name="arrow-down" size="12" />
        </div>
      </template>
      <template #right>
        <van-icon name="filter-o" @click="showFilter = true" />
      </template>
    </van-nav-bar>

    <!-- 列表 -->
    <van-pull-refresh v-model="loading" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div class="worker-list">
          <div
            v-for="worker in workerList"
            :key="worker.id"
            class="worker-card"
            @click="goDetail(worker.user_id)"
          >
            <div class="worker-header">
              <div class="worker-avatar">
                <img
                  v-if="worker.id_card_front"
                  :src="worker.id_card_front"
                  alt="头像"
                >
                <div v-else class="avatar-placeholder">
                  👤
                </div>
              </div>
              <div class="worker-basic">
                <div class="worker-name">
                  {{ worker.real_name }}
                  <van-tag
                    v-if="worker.is_available"
                    type="success"
                    size="mini"
                  >
                    可接单
                  </van-tag>
                  <van-tag
                    v-else
                    type="default"
                    size="mini"
                  >
                    休息中
                  </van-tag>
                </div>
                <div class="worker-age">
                  {{ worker.age }}岁 · {{ worker.experience_years }}年经验
                </div>
                <div class="worker-rating">
                  <van-rate
                    v-model="worker.rating"
                    :size="14"
                    color="#ffd21e"
                    void-icon="star"
                    void-color="#eee"
                    readonly
                  />
                  <span class="rating-text">{{ worker.rating }}</span>
                  <span class="order-count">({{ worker.completed_orders }}单)</span>
                </div>
              </div>
            </div>

            <div class="worker-skills">
              <van-tag
                v-for="skill in worker.skills"
                :key="skill"
                type="primary"
                plain
                size="mini"
              >
                {{ skill }}
              </van-tag>
            </div>

            <div class="worker-intro">
              {{ worker.introduction }}
            </div>

            <div class="worker-footer">
              <div class="worker-price">
                <span class="price-label">时薪</span>
                <span class="price-value">¥{{ worker.hourly_rate || '--' }}</span>
              </div>
              <van-button
                type="primary"
                size="small"
                round
                @click.stop="goDetail(worker.user_id)"
              >
                查看详情
              </van-button>
            </div>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>


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

    <!-- 筛选弹窗 -->
    <van-popup
      v-model:show="showFilter"
      position="right"
      :style="{ width: '80%', height: '100%' }"
    >
      <div class="filter-panel">
        <div class="filter-header">
          <h3>筛选条件</h3>
          <van-icon name="cross" @click="showFilter = false" />
        </div>

        <div class="filter-content">
          <div class="filter-item">
            <div class="filter-label">
              技能
            </div>
            <van-radio-group v-model="filterSkill">
              <van-radio name="">
                全部
              </van-radio>
              <van-radio name="保洁">
                保洁
              </van-radio>
              <van-radio name="月嫂">
                月嫂
              </van-radio>
              <van-radio name="育儿">
                育儿
              </van-radio>
              <van-radio name="护理">
                护理
              </van-radio>
              <van-radio name="烹饪">
                烹饪
              </van-radio>
              <van-radio name="陪护">
                陪护
              </van-radio>
            </van-radio-group>
          </div>

          <div class="filter-item">
            <div class="filter-label">
              状态
            </div>
            <van-radio-group v-model="filterAvailable">
              <van-radio :name="undefined">
                全部
              </van-radio>
              <van-radio :name="true">
                可接单
              </van-radio>
              <van-radio :name="false">
                休息中
              </van-radio>
            </van-radio-group>
          </div>
        </div>

        <div class="filter-footer">
          <van-button block @click="resetFilter">
            重置
          </van-button>
          <van-button block type="primary" @click="applyFilter">
            确定
          </van-button>
        </div>
      </div>
    </van-popup>

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
.worker-list-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #333;
  font-size: 14px;
  
  .city-name {
    max-width: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.worker-list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;

  .worker-card {
    background: #fff;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

    .worker-header {
      display: flex;
      gap: 12px;
      margin-bottom: 12px;

      .worker-avatar {
        width: 70px;
        height: 70px;
        flex-shrink: 0;
        border-radius: 8px;
        overflow: hidden;
        background: #f5f7fa;

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .avatar-placeholder {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 36px;
        }
      }

      .worker-basic {
        flex: 1;

        .worker-name {
          font-size: 16px;
          font-weight: bold;
          color: #333;
          margin-bottom: 6px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .worker-age {
          font-size: 13px;
          color: #999;
          margin-bottom: 6px;
        }

        .worker-rating {
          display: flex;
          align-items: center;
          gap: 6px;

          .rating-text {
            font-size: 13px;
            color: #ffd21e;
            font-weight: bold;
          }

          .order-count {
            font-size: 12px;
            color: #999;
          }
        }
      }
    }

    .worker-skills {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 12px;
    }

    .worker-intro {
      font-size: 14px;
      color: #666;
      line-height: 1.6;
      margin-bottom: 12px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .worker-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 12px;
      border-top: 1px solid #f5f7fa;

      .worker-price {
        .price-label {
          font-size: 13px;
          color: #999;
          margin-right: 8px;
        }

        .price-value {
          font-size: 20px;
          font-weight: bold;
          color: #FF6B6B;
        }
      }
    }
  }
}

.filter-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;

  .filter-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid #f5f7fa;

    h3 {
      font-size: 16px;
      font-weight: bold;
    }

    .van-icon {
      font-size: 20px;
      cursor: pointer;
    }
  }

  .filter-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;

    .filter-item {
      margin-bottom: 24px;

      .filter-label {
        font-size: 15px;
        font-weight: bold;
        color: #333;
        margin-bottom: 12px;
      }

      :deep(.van-radio) {
        margin-bottom: 12px;
      }
    }
  }

  .filter-footer {
    padding: 16px;
    border-top: 1px solid #f5f7fa;
    display: flex;
    gap: 12px;
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
