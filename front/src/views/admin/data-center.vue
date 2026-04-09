<template>
  <div class="data-center">
    <!-- 导航栏 -->
    <van-nav-bar title="数据中心" left-arrow @click-left="router.back()" />

    <div class="content">
      <!-- 数据导出 -->
      <div class="section">
        <div class="section-title">
          <van-icon name="down" />
          <span>数据导出</span>
        </div>
        
        <van-cell-group inset>
          <van-cell title="导出阿姨名单" is-link @click="showExportWorkers = true">
            <template #icon>
              <van-icon name="friends" class="cell-icon" />
            </template>
            <template #label>
              <span class="cell-desc">导出所有阿姨信息为Excel</span>
            </template>
          </van-cell>
          
          <van-cell title="导出用户列表" is-link @click="showExportUsers = true">
            <template #icon>
              <van-icon name="user" class="cell-icon" />
            </template>
            <template #label>
              <span class="cell-desc">导出所有用户信息为Excel</span>
            </template>
          </van-cell>
          
          <van-cell title="导出订单数据" is-link @click="showExportOrders = true">
            <template #icon>
              <van-icon name="orders-o" class="cell-icon" />
            </template>
            <template #label>
              <span class="cell-desc">导出订单记录为Excel</span>
            </template>
          </van-cell>
          
          <van-cell title="导出统计报告" is-link @click="handleExportStatistics">
            <template #icon>
              <van-icon name="chart-trending-o" class="cell-icon" />
            </template>
            <template #label>
              <span class="cell-desc">导出平台数据统计报告</span>
            </template>
          </van-cell>
        </van-cell-group>
      </div>

      <!-- 数据导入 -->
      <div class="section">
        <div class="section-title">
          <van-icon name="upgrade" />
          <span>数据导入</span>
        </div>
        
        <van-cell-group inset>
          <van-cell title="批量导入阿姨" is-link @click="showImportWorkers = true">
            <template #icon>
              <van-icon name="friends" class="cell-icon" />
            </template>
            <template #label>
              <span class="cell-desc">通过Excel批量添加阿姨</span>
            </template>
          </van-cell>
          
          <van-cell title="批量导入用户" is-link @click="showImportUsers = true">
            <template #icon>
              <van-icon name="user" class="cell-icon" />
            </template>
            <template #label>
              <span class="cell-desc">通过Excel批量添加用户</span>
            </template>
          </van-cell>
        </van-cell-group>
      </div>

      <!-- 使用说明 -->
      <div class="section">
        <div class="section-title">
          <van-icon name="info-o" />
          <span>使用说明</span>
        </div>
        
        <van-cell-group inset>
          <div class="tips">
            <p>1. 导出的Excel文件包含筛选条件内的所有数据</p>
            <p>2. 导入前请先下载模板，按模板格式填写数据</p>
            <p>3. 批量导入的用户默认密码为 <code>123456</code></p>
            <p>4. 导入时会自动跳过重复的手机号和邮箱</p>
          </div>
        </van-cell-group>
      </div>
    </div>

    <!-- 导出阿姨弹窗 -->
    <van-action-sheet v-model:show="showExportWorkers" title="导出阿姨名单">
      <div class="export-options">
        <van-cell-group>
          <van-cell title="筛选条件" />
          <van-cell title="接单状态">
            <template #value>
              <van-radio-group v-model="exportWorkerFilter.is_available" direction="horizontal">
                <van-radio name="">全部</van-radio>
                <van-radio name="true">接单中</van-radio>
                <van-radio name="false">休息中</van-radio>
              </van-radio-group>
            </template>
          </van-cell>
          <van-cell title="推荐状态">
            <template #value>
              <van-radio-group v-model="exportWorkerFilter.is_recommended" direction="horizontal">
                <van-radio name="">全部</van-radio>
                <van-radio name="true">已推荐</van-radio>
                <van-radio name="false">未推荐</van-radio>
              </van-radio-group>
            </template>
          </van-cell>
        </van-cell-group>
        <div class="action-btn">
          <van-button type="primary" block :loading="exporting" @click="handleExportWorkers">
            确认导出
          </van-button>
        </div>
      </div>
    </van-action-sheet>

    <!-- 导出用户弹窗 -->
    <van-action-sheet v-model:show="showExportUsers" title="导出用户列表">
      <div class="export-options">
        <van-cell-group>
          <van-cell title="筛选条件" />
          <van-cell title="用户角色">
            <template #value>
              <van-radio-group v-model="exportUserFilter.role" direction="horizontal">
                <van-radio name="">全部</van-radio>
                <van-radio name="user">普通用户</van-radio>
                <van-radio name="worker">阿姨</van-radio>
              </van-radio-group>
            </template>
          </van-cell>
          <van-cell title="账号状态">
            <template #value>
              <van-radio-group v-model="exportUserFilter.status" direction="horizontal">
                <van-radio name="">全部</van-radio>
                <van-radio name="active">正常</van-radio>
                <van-radio name="disabled">禁用</van-radio>
              </van-radio-group>
            </template>
          </van-cell>
        </van-cell-group>
        <div class="action-btn">
          <van-button type="primary" block :loading="exporting" @click="handleExportUsers">
            确认导出
          </van-button>
        </div>
      </div>
    </van-action-sheet>

    <!-- 导出订单弹窗 -->
    <van-action-sheet v-model:show="showExportOrders" title="导出订单数据">
      <div class="export-options">
        <van-cell-group>
          <van-cell title="筛选条件" />
          <van-cell title="订单状态">
            <template #value>
              <van-radio-group v-model="exportOrderFilter.status" direction="horizontal">
                <van-radio name="">全部</van-radio>
                <van-radio name="pending">待接单</van-radio>
                <van-radio name="completed">已完成</van-radio>
              </van-radio-group>
            </template>
          </van-cell>
          <van-cell title="开始日期" is-link @click="showStartDatePicker = true">
            <template #value>
              {{ exportOrderFilter.start_date || '不限' }}
            </template>
          </van-cell>
          <van-cell title="结束日期" is-link @click="showEndDatePicker = true">
            <template #value>
              {{ exportOrderFilter.end_date || '不限' }}
            </template>
          </van-cell>
        </van-cell-group>
        <div class="action-btn">
          <van-button type="primary" block :loading="exporting" @click="handleExportOrders">
            确认导出
          </van-button>
        </div>
      </div>
    </van-action-sheet>

    <!-- 日期选择器 -->
    <van-popup v-model:show="showStartDatePicker" position="bottom" round>
      <van-date-picker
        title="选择开始日期"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="onStartDateConfirm"
        @cancel="showStartDatePicker = false"
      />
    </van-popup>
    <van-popup v-model:show="showEndDatePicker" position="bottom" round>
      <van-date-picker
        title="选择结束日期"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="onEndDateConfirm"
        @cancel="showEndDatePicker = false"
      />
    </van-popup>

    <!-- 导入阿姨弹窗 -->
    <van-action-sheet v-model:show="showImportWorkers" title="批量导入阿姨">
      <div class="import-options">
        <div class="step">
          <div class="step-num">1</div>
          <div class="step-content">
            <p class="step-title">下载模板</p>
            <p class="step-desc">请先下载Excel模板，按格式填写数据</p>
            <van-button size="small" plain type="primary" @click="handleDownloadWorkerTemplate">
              下载模板
            </van-button>
          </div>
        </div>
        <div class="step">
          <div class="step-num">2</div>
          <div class="step-content">
            <p class="step-title">上传文件</p>
            <p class="step-desc">选择填写好的Excel文件上传</p>
            <van-uploader
              v-model="workerFiles"
              :max-count="1"
              accept=".xlsx,.xls"
              :after-read="handleWorkerFileSelect"
            >
              <van-button size="small" plain type="primary">选择文件</van-button>
            </van-uploader>
          </div>
        </div>
        <div class="action-btn">
          <van-button 
            type="primary" 
            block 
            :loading="importing" 
            :disabled="!selectedWorkerFile"
            @click="handleImportWorkers"
          >
            开始导入
          </van-button>
        </div>
      </div>
    </van-action-sheet>

    <!-- 导入用户弹窗 -->
    <van-action-sheet v-model:show="showImportUsers" title="批量导入用户">
      <div class="import-options">
        <div class="step">
          <div class="step-num">1</div>
          <div class="step-content">
            <p class="step-title">下载模板</p>
            <p class="step-desc">请先下载Excel模板，按格式填写数据</p>
            <van-button size="small" plain type="primary" @click="handleDownloadUserTemplate">
              下载模板
            </van-button>
          </div>
        </div>
        <div class="step">
          <div class="step-num">2</div>
          <div class="step-content">
            <p class="step-title">上传文件</p>
            <p class="step-desc">选择填写好的Excel文件上传</p>
            <van-uploader
              v-model="userFiles"
              :max-count="1"
              accept=".xlsx,.xls"
              :after-read="handleUserFileSelect"
            >
              <van-button size="small" plain type="primary">选择文件</van-button>
            </van-uploader>
          </div>
        </div>
        <div class="action-btn">
          <van-button 
            type="primary" 
            block 
            :loading="importing" 
            :disabled="!selectedUserFile"
            @click="handleImportUsers"
          >
            开始导入
          </van-button>
        </div>
      </div>
    </van-action-sheet>

    <!-- 导入结果弹窗 -->
    <van-dialog
      v-model:show="showImportResult"
      title="导入结果"
      :show-cancel-button="false"
    >
      <div class="import-result">
        <div class="result-item success">
          <van-icon name="success" />
          <span>成功：{{ importResult.success }} 条</span>
        </div>
        <div class="result-item fail" v-if="importResult.failed > 0">
          <van-icon name="cross" />
          <span>失败：{{ importResult.failed }} 条</span>
        </div>
        <div class="error-list" v-if="importResult.errors?.length">
          <p class="error-title">错误详情：</p>
          <p v-for="(err, idx) in importResult.errors.slice(0, 5)" :key="idx" class="error-item">
            {{ err }}
          </p>
          <p v-if="importResult.errors.length > 5" class="error-more">
            ...还有 {{ importResult.errors.length - 5 }} 条错误
          </p>
        </div>
      </div>
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showLoadingToast, closeToast } from 'vant'
import adminApi from '@/api/modules/admin'

const router = useRouter()

// 导出相关
const showExportWorkers = ref(false)
const showExportUsers = ref(false)
const showExportOrders = ref(false)
const exporting = ref(false)

// 日期选择器
const showStartDatePicker = ref(false)
const showEndDatePicker = ref(false)
const minDate = new Date(2024, 0, 1)
const maxDate = new Date()

const exportWorkerFilter = ref({
  is_available: '',
  is_recommended: ''
})

const exportUserFilter = ref({
  role: '',
  status: ''
})

const exportOrderFilter = ref({
  status: '',
  start_date: '',
  end_date: ''
})

// 导入相关
const showImportWorkers = ref(false)
const showImportUsers = ref(false)
const importing = ref(false)
const workerFiles = ref<any[]>([])
const userFiles = ref<any[]>([])
const selectedWorkerFile = ref<File | null>(null)
const selectedUserFile = ref<File | null>(null)

// 导入结果
const showImportResult = ref(false)
const importResult = ref<{
  success: number
  failed: number
  errors: string[]
}>({ success: 0, failed: 0, errors: [] })

// 下载文件通用方法
const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// 导出阿姨
const handleExportWorkers = async () => {
  exporting.value = true
  try {
    const params: any = {}
    if (exportWorkerFilter.value.is_available) {
      params.is_available = exportWorkerFilter.value.is_available === 'true'
    }
    if (exportWorkerFilter.value.is_recommended) {
      params.is_recommended = exportWorkerFilter.value.is_recommended === 'true'
    }
    
    const res = await adminApi.exportWorkers(params)
    downloadBlob(res.data, `阿姨名单_${new Date().toLocaleDateString()}.xlsx`)
    showExportWorkers.value = false
    showToast('导出成功')
  } catch (e: any) {
    showToast(e.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

// 导出用户
const handleExportUsers = async () => {
  exporting.value = true
  try {
    const params: any = {}
    if (exportUserFilter.value.role) params.role = exportUserFilter.value.role
    if (exportUserFilter.value.status) params.status = exportUserFilter.value.status
    
    const res = await adminApi.exportUsers(params)
    downloadBlob(res.data, `用户列表_${new Date().toLocaleDateString()}.xlsx`)
    showExportUsers.value = false
    showToast('导出成功')
  } catch (e: any) {
    showToast(e.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

// 导出订单
const handleExportOrders = async () => {
  exporting.value = true
  try {
    const params: any = {}
    if (exportOrderFilter.value.status) params.status = exportOrderFilter.value.status
    if (exportOrderFilter.value.start_date) params.start_date = exportOrderFilter.value.start_date
    if (exportOrderFilter.value.end_date) params.end_date = exportOrderFilter.value.end_date
    
    const res = await adminApi.exportOrders(params)
    downloadBlob(res.data, `订单数据_${new Date().toLocaleDateString()}.xlsx`)
    showExportOrders.value = false
    showToast('导出成功')
  } catch (e: any) {
    showToast(e.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

// 日期选择确认
const onStartDateConfirm = ({ selectedValues }: { selectedValues: string[] }) => {
  exportOrderFilter.value.start_date = selectedValues.join('-')
  showStartDatePicker.value = false
}

const onEndDateConfirm = ({ selectedValues }: { selectedValues: string[] }) => {
  exportOrderFilter.value.end_date = selectedValues.join('-')
  showEndDatePicker.value = false
}

// 导出统计报告
const handleExportStatistics = async () => {
  showLoadingToast({ message: '导出中...', forbidClick: true })
  try {
    const res = await adminApi.exportStatistics()
    downloadBlob(res.data, `平台统计报告_${new Date().toLocaleDateString()}.xlsx`)
    closeToast()
    showToast('导出成功')
  } catch (e: any) {
    closeToast()
    showToast(e.message || '导出失败')
  }
}

// 下载阿姨模板
const handleDownloadWorkerTemplate = async () => {
  try {
    const res = await adminApi.downloadWorkerTemplate()
    downloadBlob(res.data, '阿姨导入模板.xlsx')
  } catch (e: any) {
    showToast(e.message || '下载失败')
  }
}

// 下载用户模板
const handleDownloadUserTemplate = async () => {
  try {
    const res = await adminApi.downloadUserTemplate()
    downloadBlob(res.data, '用户导入模板.xlsx')
  } catch (e: any) {
    showToast(e.message || '下载失败')
  }
}

// 选择阿姨文件
const handleWorkerFileSelect = (file: any) => {
  selectedWorkerFile.value = file.file
}

// 选择用户文件
const handleUserFileSelect = (file: any) => {
  selectedUserFile.value = file.file
}

// 导入阿姨
const handleImportWorkers = async () => {
  if (!selectedWorkerFile.value) return
  
  importing.value = true
  try {
    const res = await adminApi.importWorkers(selectedWorkerFile.value)
    // res 已经是 { code, message, data } 格式
    importResult.value = res.data
    showImportWorkers.value = false
    showImportResult.value = true
    // 清空文件
    workerFiles.value = []
    selectedWorkerFile.value = null
  } catch (e: any) {
    showToast(e.message || '导入失败')
  } finally {
    importing.value = false
  }
}

// 导入用户
const handleImportUsers = async () => {
  if (!selectedUserFile.value) return
  
  importing.value = true
  try {
    const res = await adminApi.importUsers(selectedUserFile.value)
    // res 已经是 { code, message, data } 格式
    importResult.value = res.data
    showImportUsers.value = false
    showImportResult.value = true
    // 清空文件
    userFiles.value = []
    selectedUserFile.value = null
  } catch (e: any) {
    showToast(e.message || '导入失败')
  } finally {
    importing.value = false
  }
}
</script>

<style scoped lang="scss">
.data-center {
  min-height: 100vh;
  background: #f7f8fa;
}

.content {
  padding: 12px;
}

.section {
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  color: #323233;
  
  .van-icon {
    color: #ff9f43;
  }
}

.cell-icon {
  margin-right: 8px;
  color: #ff9f43;
}

.cell-desc {
  font-size: 12px;
  color: #969799;
}

.tips {
  padding: 12px 16px;
  font-size: 13px;
  color: #646566;
  line-height: 1.8;
  
  code {
    background: #fff3e0;
    color: #ff9f43;
    padding: 2px 6px;
    border-radius: 4px;
  }
}

.export-options,
.import-options {
  padding: 16px;
}

.action-btn {
  margin-top: 20px;
}

.step {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  
  .step-num {
    width: 24px;
    height: 24px;
    background: #ff9f43;
    color: #fff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 500;
    flex-shrink: 0;
  }
  
  .step-content {
    flex: 1;
    
    .step-title {
      font-size: 15px;
      font-weight: 500;
      color: #323233;
      margin-bottom: 4px;
    }
    
    .step-desc {
      font-size: 13px;
      color: #969799;
      margin-bottom: 8px;
    }
  }
}

.import-result {
  padding: 16px;
  
  .result-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 0;
    font-size: 15px;
    
    &.success {
      color: #07c160;
    }
    
    &.fail {
      color: #ee0a24;
    }
  }
  
  .error-list {
    margin-top: 12px;
    padding: 12px;
    background: #fff7f7;
    border-radius: 8px;
    
    .error-title {
      font-size: 13px;
      color: #ee0a24;
      margin-bottom: 8px;
    }
    
    .error-item {
      font-size: 12px;
      color: #646566;
      line-height: 1.6;
    }
    
    .error-more {
      font-size: 12px;
      color: #969799;
      margin-top: 4px;
    }
  }
}
</style>
