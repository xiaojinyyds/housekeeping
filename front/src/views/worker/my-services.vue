<script setup lang="ts">
import { showToast, showLoadingToast, closeToast, showConfirmDialog } from 'vant'
import apiWorker from '@/api/modules/worker'

definePage({
  name: 'worker-my-services',
  meta: {
    title: '服务管理',
  },
})

const router = useRouter()

const loading = ref(true)
const allServices = ref<any[]>([])
const myServices = ref<any[]>([])
const showPriceDialog = ref(false)
const currentService = ref<any>(null)
const editPrice = ref<number>(0)

// 获取数据
async function fetchData() {
  loading.value = true
  try {
    const [allRes, myRes]: any[] = await Promise.all([
      apiWorker.getAllServices(),
      apiWorker.getMyServices(),
    ])

    if (allRes.code === 200) {
      allServices.value = allRes.data || []
    }
    if (myRes.code === 200) {
      myServices.value = myRes.data || []
    }
  }
  catch (error: any) {
    console.error('获取服务失败:', error)
    if (error.response?.status === 403) {
      showToast('您不是家政阿姨')
      router.back()
    }
  }
  finally {
    loading.value = false
  }
}

// 检查服务是否已添加
function isServiceAdded(serviceId: string) {
  return myServices.value.some(s => s.service_id === serviceId)
}

// 获取我的服务定价
function getMyServicePrice(serviceId: string) {
  const myService = myServices.value.find(s => s.service_id === serviceId)
  return myService?.price
}

// 打开定价弹窗
function openPriceDialog(service: any) {
  currentService.value = service
  editPrice.value = getMyServicePrice(service.id) || service.price || 0
  showPriceDialog.value = true
}

// 保存服务
async function saveService() {
  if (!currentService.value)
    return
  if (editPrice.value <= 0) {
    showToast('请输入有效价格')
    return
  }

  showLoadingToast({ message: '保存中...', forbidClick: true })

  try {
    const res: any = await apiWorker.addMyService({
      service_id: currentService.value.id,
      price: editPrice.value,
      is_active: true,
    })

    closeToast()

    if (res.code === 200) {
      showToast('保存成功')
      showPriceDialog.value = false
      fetchData() // 刷新数据
    }
    else {
      showToast(res.message || '保存失败')
    }
  }
  catch (error) {
    closeToast()
    showToast('保存失败')
  }
}

// 移除服务
async function removeService(serviceId: string) {
  try {
    await showConfirmDialog({
      title: '确认移除',
      message: '确定要移除这项服务吗？',
    })

    showLoadingToast({ message: '移除中...', forbidClick: true })

    const res: any = await apiWorker.removeMyService(serviceId)

    closeToast()

    if (res.code === 200) {
      showToast('已移除')
      fetchData()
    }
    else {
      showToast(res.message || '移除失败')
    }
  }
  catch {
    // 用户取消
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="my-services-page">
    <!-- 顶部导航 -->
    <van-nav-bar
      title="服务管理"
      left-arrow
      @click-left="router.back()"
    />

    <van-loading v-if="loading" class="page-loading" />

    <template v-else>
      <!-- 我的服务 -->
      <div v-if="myServices.length > 0" class="section">
        <div class="section-title">
          我提供的服务
        </div>
        <div class="service-list">
          <div
            v-for="item in myServices"
            :key="item.id"
            class="service-item my-service"
          >
            <div class="icon-wrapper">
              <van-icon :name="item.service_icon || 'star-o'" size="24" color="#FF9F43" />
            </div>
            <div class="content">
              <div class="name">
                {{ item.service_name }}
              </div>
              <div class="category">
                {{ item.service_category }}
              </div>
            </div>
            <div class="price-info">
              <div class="price">
                ¥{{ item.price }}<span class="unit">/{{ item.unit }}</span>
              </div>
              <div class="actions">
                <van-button
                  size="mini"
                  plain
                  @click="openPriceDialog({ id: item.service_id, name: item.service_name, price: item.default_price })"
                >
                  修改
                </van-button>
                <van-button
                  size="mini"
                  plain
                  type="danger"
                  @click="removeService(item.service_id)"
                >
                  移除
                </van-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 可添加的服务 -->
      <div class="section">
        <div class="section-title">
          可提供的服务项目
        </div>
        <div class="service-list">
          <div
            v-for="service in allServices"
            :key="service.id"
            class="service-item"
            :class="{ added: isServiceAdded(service.id) }"
          >
            <div class="icon-wrapper" :class="{ active: isServiceAdded(service.id) }">
              <van-icon :name="service.icon || 'star-o'" size="24" />
            </div>
            <div class="content">
              <div class="name">
                {{ service.name }}
                <van-tag v-if="isServiceAdded(service.id)" type="success" size="mini">
                  已添加
                </van-tag>
              </div>
              <div class="desc">
                {{ service.description }}
              </div>
              <div class="ref-price">
                参考价：¥{{ service.price }}/{{ service.unit }}
              </div>
            </div>
            <van-button
              v-if="!isServiceAdded(service.id)"
              size="small"
              type="primary"
              plain
              @click="openPriceDialog(service)"
            >
              添加
            </van-button>
          </div>
        </div>
      </div>
    </template>

    <!-- 定价弹窗 -->
    <van-dialog
      v-model:show="showPriceDialog"
      :title="`设置 ${currentService?.name} 价格`"
      show-cancel-button
      @confirm="saveService"
    >
      <div class="price-dialog-content">
        <van-field
          v-model.number="editPrice"
          type="number"
          label="服务价格"
          placeholder="请输入价格"
          :rules="[{ required: true, message: '请输入价格' }]"
        >
          <template #button>
            <span class="unit-text">元</span>
          </template>
        </van-field>
        <div v-if="currentService?.price" class="ref-tip">
          参考价格：¥{{ currentService.price }}
        </div>
      </div>
    </van-dialog>
  </div>
</template>

<style scoped lang="scss">
.my-services-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.page-loading {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

.section {
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
}

.service-list {
  display: flex;
  flex-direction: column;
  gap: 12px;

  .service-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 14px;
    background: #fafafa;
    border-radius: 10px;
    border: 1px solid transparent;

    &.added {
      border-color: #e8f5e9;
      background: #f1f8e9;
    }

    &.my-service {
      border-color: #fff3e0;
      background: #fff8e1;
    }

    .icon-wrapper {
      width: 44px;
      height: 44px;
      border-radius: 10px;
      background: #f0f0f0;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #999;
      flex-shrink: 0;

      &.active {
        background: rgba(255, 159, 67, 0.15);
        color: #FF9F43;
      }
    }

    .content {
      flex: 1;
      min-width: 0;

      .name {
        font-size: 15px;
        font-weight: 500;
        color: #333;
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 4px;
      }

      .desc {
        font-size: 12px;
        color: #666;
        margin-bottom: 4px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
      }

      .category {
        font-size: 12px;
        color: #999;
      }

      .ref-price {
        font-size: 12px;
        color: #FF9F43;
      }
    }

    .price-info {
      flex-shrink: 0;
      text-align: right;

      .price {
        font-size: 16px;
        font-weight: bold;
        color: #FF9F43;
        margin-bottom: 8px;

        .unit {
          font-size: 12px;
          font-weight: normal;
          color: #999;
        }
      }

      .actions {
        display: flex;
        gap: 6px;
      }
    }
  }
}

.price-dialog-content {
  padding: 16px;

  .ref-tip {
    font-size: 13px;
    color: #999;
    margin-top: 8px;
    padding-left: 8px;
  }

  .unit-text {
    color: #666;
  }
}
</style>
