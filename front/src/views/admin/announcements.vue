<script setup lang="ts">
import { showToast, showConfirmDialog } from 'vant'
import apiAnnouncement from '@/api/modules/announcement'
import apiUpload from '@/api/modules/upload'

definePage({
  name: 'admin-announcements',
  meta: {
    title: '公告管理',
    auth: true,
  },
})

const router = useRouter()
const userStore = useUserStore()

// 检查权限
if (!userStore.isAdmin) {
  showToast('无权访问')
  router.replace('/')
}

const loading = ref(false)
const finished = ref(false)
const announcementList = ref<any[]>([])
const page = ref(1)
const pageSize = 10

// 筛选条件
const activeTab = ref('all')
const tabs = [
  { name: 'all', title: '全部' },
  { name: 'published', title: '已发布' },
  { name: 'draft', title: '草稿' },
]

// 搜索关键词
const searchKeyword = ref('')

// 获取公告列表
async function getAnnouncements(isRefresh = false) {
  if (isRefresh) {
    page.value = 1
    announcementList.value = []
    finished.value = false
  }

  loading.value = true
  try {
    const params: any = {
      page: page.value,
      page_size: pageSize,
      keyword: searchKeyword.value || undefined,
    }

    if (activeTab.value === 'published') {
      params.is_published = true
    } else if (activeTab.value === 'draft') {
      params.is_published = false
    }

    const res: any = await apiAnnouncement.adminGetList(params)

    if (res.code === 200) {
      if (isRefresh) {
        announcementList.value = res.data.list
      } else {
        announcementList.value.push(...res.data.list)
      }

      if (res.data.list.length < pageSize) {
        finished.value = true
      } else {
        page.value++
      }
    }
  } catch (error: any) {
    showToast(error.message || '加载失败')
    finished.value = true
  } finally {
    loading.value = false
  }
}

// 切换标签
function onTabChange() {
  getAnnouncements(true)
}

// 搜索
function onSearch() {
  getAnnouncements(true)
}

// 下拉刷新
async function onRefresh() {
  await getAnnouncements(true)
}

// 上拉加载
async function onLoad() {
  await getAnnouncements()
}

// 类型文本
function getTypeText(type: string) {
  const texts: any = {
    notice: '通知',
    activity: '活动',
    system: '系统',
  }
  return texts[type] || type
}

// 类型颜色
function getTypeColor(type: string) {
  const colors: any = {
    notice: '#1989FA',
    activity: '#07C160',
    system: '#FF9F43',
  }
  return colors[type] || '#999'
}

// ========== 创建/编辑公告 ==========
const showDialog = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const dialogTitle = computed(() => dialogMode.value === 'create' ? '创建公告' : '编辑公告')
const currentAnnouncement = ref<any>(null)

const dialogForm = reactive({
  title: '',
  content: '',
  cover_image: '',
  type: 'notice',
  is_top: false,
  expire_time: '',
})

const showTypePicker = ref(false)
const showDatePicker = ref(false)
const uploading = ref(false)

// 打开创建对话框
function openCreateDialog() {
  dialogMode.value = 'create'
  dialogForm.title = ''
  dialogForm.content = ''
  dialogForm.cover_image = ''
  dialogForm.type = 'notice'
  dialogForm.is_top = false
  dialogForm.expire_time = ''
  showDialog.value = true
}

// 打开编辑对话框
function openEditDialog(item: any) {
  dialogMode.value = 'edit'
  currentAnnouncement.value = item
  dialogForm.title = item.title
  dialogForm.content = item.content
  dialogForm.cover_image = item.cover_image || ''
  dialogForm.type = item.type
  dialogForm.is_top = item.is_top
  dialogForm.expire_time = item.expire_time ? item.expire_time.split('T')[0] : ''
  showDialog.value = true
}

// 上传封面图
async function onUploadCover(file: any) {
  uploading.value = true
  try {
    const res: any = await apiUpload.uploadImage(file.file)
    if (res.code === 200) {
      dialogForm.cover_image = res.data.url
      showToast('上传成功')
    }
  } catch (error: any) {
    showToast(error.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

// 删除封面图
function removeCover() {
  dialogForm.cover_image = ''
}

// 提交表单
async function submitDialog() {
  if (!dialogForm.title) {
    showToast('请输入标题')
    return
  }
  if (!dialogForm.content) {
    showToast('请输入内容')
    return
  }

  try {
    const data: any = {
      title: dialogForm.title,
      content: dialogForm.content,
      cover_image: dialogForm.cover_image || undefined,
      type: dialogForm.type,
      is_top: dialogForm.is_top,
      expire_time: dialogForm.expire_time || undefined,
    }

    if (dialogMode.value === 'create') {
      const res: any = await apiAnnouncement.create(data)
      if (res.code === 200) {
        showToast('创建成功')
        showDialog.value = false
        getAnnouncements(true)
      }
    } else {
      const res: any = await apiAnnouncement.update(currentAnnouncement.value.id, data)
      if (res.code === 200) {
        showToast('更新成功')
        showDialog.value = false
        getAnnouncements(true)
      }
    }
  } catch (error: any) {
    showToast(error.message || '操作失败')
  }
}

// 发布/取消发布
async function togglePublish(item: any) {
  const action = item.is_published ? '取消发布' : '发布'
  try {
    await showConfirmDialog({
      title: `确认${action}`,
      message: `确定要${action}公告「${item.title}」吗？`,
    })

    const res: any = item.is_published
      ? await apiAnnouncement.unpublish(item.id)
      : await apiAnnouncement.publish(item.id)

    if (res.code === 200) {
      showToast(`${action}成功`)
      item.is_published = !item.is_published
      if (!item.is_published) {
        item.publish_time = null
      } else {
        item.publish_time = res.data.publish_time
      }
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      showToast(error.message || '操作失败')
    }
  }
}

// 删除公告
async function deleteAnnouncement(item: any) {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: `确定要删除公告「${item.title}」吗？此操作不可恢复！`,
    })

    const res: any = await apiAnnouncement.delete(item.id)
    if (res.code === 200) {
      showToast('删除成功')
      getAnnouncements(true)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      showToast(error.message || '操作失败')
    }
  }
}

// 日期选择确认
function onDateConfirm(value: any) {
  const date = value.selectedValues.join('-')
  dialogForm.expire_time = date
  showDatePicker.value = false
}

// 清除过期时间
function clearExpireTime() {
  dialogForm.expire_time = ''
}

onMounted(() => {
  getAnnouncements(true)
})
</script>

<template>
  <div class="admin-announcements-page">
    <van-nav-bar
      title="公告管理"
      left-arrow
      @click-left="router.back()"
      class="nav-bar"
    >
      <template #right>
        <van-icon name="plus" size="20" @click="openCreateDialog" />
      </template>
    </van-nav-bar>

    <!-- 搜索栏 -->
    <div class="search-section">
      <van-search
        v-model="searchKeyword"
        placeholder="搜索公告标题/内容"
        @search="onSearch"
        @clear="onSearch"
      />
    </div>

    <!-- 标签页 -->
    <van-tabs v-model:active="activeTab" @change="onTabChange" sticky>
      <van-tab
        v-for="tab in tabs"
        :key="tab.name"
        :name="tab.name"
        :title="tab.title"
      >
        <van-pull-refresh v-model="loading" @refresh="onRefresh">
          <van-list
            v-model:loading="loading"
            :finished="finished"
            finished-text="没有更多了"
            @load="onLoad"
          >
            <div class="announcement-list">
              <div
                v-for="item in announcementList"
                :key="item.id"
                class="announcement-card"
              >
                <!-- 卡片头部 -->
                <div class="card-header">
                  <div class="title-row">
                    <van-tag v-if="item.is_top" type="danger">置顶</van-tag>
                    <span class="title">{{ item.title }}</span>
                  </div>
                  <div class="meta-row">
                    <van-tag plain :color="getTypeColor(item.type)">
                      {{ getTypeText(item.type) }}
                    </van-tag>
                    <van-tag
                      :type="item.is_published ? 'success' : 'default'"
                      style="margin-left: 6px;"
                    >
                      {{ item.is_published ? '已发布' : '草稿' }}
                    </van-tag>
                  </div>
                </div>

                <!-- 封面图 -->
                <div v-if="item.cover_image" class="cover-image">
                  <van-image
                    :src="item.cover_image"
                    width="100%"
                    height="120"
                    fit="cover"
                    radius="8"
                  />
                </div>

                <!-- 内容预览 -->
                <div class="content-preview">
                  {{ item.content.substring(0, 100) }}{{ item.content.length > 100 ? '...' : '' }}
                </div>

                <!-- 卡片信息 -->
                <div class="card-info">
                  <div class="info-item">
                    <van-icon name="eye-o" size="14" color="#999" />
                    <span>{{ item.view_count || 0 }} 次浏览</span>
                  </div>
                  <div class="info-item">
                    <van-icon name="clock-o" size="14" color="#999" />
                    <span>{{ new Date(item.created_at).toLocaleDateString() }}</span>
                  </div>
                  <div v-if="item.expire_time" class="info-item">
                    <van-icon name="underway-o" size="14" color="#999" />
                    <span>过期: {{ new Date(item.expire_time).toLocaleDateString() }}</span>
                  </div>
                </div>

                <!-- 卡片操作 -->
                <div class="card-footer">
                  <van-button
                    size="small"
                    plain
                    type="primary"
                    @click="openEditDialog(item)"
                  >
                    编辑
                  </van-button>
                  <van-button
                    size="small"
                    plain
                    :type="item.is_published ? 'warning' : 'success'"
                    @click="togglePublish(item)"
                  >
                    {{ item.is_published ? '取消发布' : '发布' }}
                  </van-button>
                  <van-button
                    size="small"
                    plain
                    type="danger"
                    @click="deleteAnnouncement(item)"
                  >
                    删除
                  </van-button>
                </div>
              </div>

              <!-- 空状态 -->
              <van-empty
                v-if="!loading && announcementList.length === 0"
                description="暂无公告"
              />
            </div>
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>

    <!-- 创建/编辑公告弹窗 -->
    <van-popup
      v-model:show="showDialog"
      position="bottom"
      round
      :style="{ height: '90%' }"
      closeable
    >
      <div class="dialog-content">
        <div class="dialog-header">
          <span class="dialog-title">{{ dialogTitle }}</span>
        </div>

        <div class="dialog-body">
          <van-cell-group inset>
            <van-field
              v-model="dialogForm.title"
              label="标题"
              placeholder="请输入公告标题"
              required
              maxlength="100"
              show-word-limit
            />

            <van-field
              v-model="dialogForm.type"
              label="类型"
              readonly
              clickable
              @click="showTypePicker = true"
            >
              <template #input>
                <van-tag plain :color="getTypeColor(dialogForm.type)">
                  {{ getTypeText(dialogForm.type) }}
                </van-tag>
              </template>
            </van-field>

            <van-field label="封面图">
              <template #input>
                <div class="cover-upload">
                  <van-uploader
                    v-if="!dialogForm.cover_image"
                    :after-read="onUploadCover"
                    :max-count="1"
                    accept="image/*"
                    :disabled="uploading"
                  >
                    <van-button
                      size="small"
                      icon="photo"
                      :loading="uploading"
                    >
                      上传封面
                    </van-button>
                  </van-uploader>
                  <div v-else class="cover-preview">
                    <van-image
                      :src="dialogForm.cover_image"
                      width="80"
                      height="60"
                      fit="cover"
                      radius="4"
                    />
                    <van-icon
                      name="clear"
                      class="remove-icon"
                      @click="removeCover"
                    />
                  </div>
                </div>
              </template>
            </van-field>

            <van-field
              v-model="dialogForm.content"
              label="内容"
              type="textarea"
              placeholder="请输入公告内容"
              required
              rows="6"
              autosize
              maxlength="5000"
              show-word-limit
            />

            <van-field label="过期时间">
              <template #input>
                <div class="expire-time-field">
                  <span
                    v-if="dialogForm.expire_time"
                    class="expire-time-value"
                    @click="showDatePicker = true"
                  >
                    {{ dialogForm.expire_time }}
                  </span>
                  <span
                    v-else
                    class="expire-time-placeholder"
                    @click="showDatePicker = true"
                  >
                    永不过期
                  </span>
                  <van-icon
                    v-if="dialogForm.expire_time"
                    name="clear"
                    class="clear-icon"
                    @click="clearExpireTime"
                  />
                </div>
              </template>
            </van-field>

            <van-cell title="置顶" center>
              <template #right-icon>
                <van-switch v-model="dialogForm.is_top" size="20" />
              </template>
            </van-cell>
          </van-cell-group>
        </div>

        <div class="dialog-footer">
          <van-button block type="primary" @click="submitDialog">
            {{ dialogMode === 'create' ? '创建' : '保存' }}
          </van-button>
        </div>
      </div>
    </van-popup>

    <!-- 类型选择器 -->
    <van-popup v-model:show="showTypePicker" position="bottom" round>
      <van-picker
        :columns="[
          { text: '通知', value: 'notice' },
          { text: '活动', value: 'activity' },
          { text: '系统', value: 'system' },
        ]"
        @confirm="(value: any) => { dialogForm.type = value.selectedOptions[0].value; showTypePicker = false }"
        @cancel="showTypePicker = false"
      />
    </van-popup>

    <!-- 日期选择器 -->
    <van-popup v-model:show="showDatePicker" position="bottom" round>
      <van-date-picker
        :min-date="new Date()"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>
  </div>
</template>


<style scoped lang="scss">
.admin-announcements-page {
  min-height: 100vh;
  background: #F7F8FA;
}

.nav-bar {
  background: linear-gradient(135deg, #FF9F43 0%, #FF7F50 100%);

  :deep(.van-nav-bar__title) {
    color: #fff;
  }

  :deep(.van-icon) {
    color: #fff;
  }
}

.search-section {
  background: #fff;
  padding: 8px 0;

  :deep(.van-search) {
    padding: 8px 16px;
  }
}

:deep(.van-tabs) {
  .van-tabs__nav {
    background: #fff;
  }

  .van-tab {
    color: #666;
    font-size: 15px;

    &--active {
      color: #FF9F43;
      font-weight: bold;
    }
  }

  .van-tabs__line {
    background: #FF9F43;
  }
}

.announcement-list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;

  .announcement-card {
    background: #fff;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

    .card-header {
      margin-bottom: 12px;

      .title-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        .title {
          font-size: 16px;
          font-weight: bold;
          color: #333;
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      .meta-row {
        display: flex;
        align-items: center;
      }
    }

    .cover-image {
      margin-bottom: 12px;
    }

    .content-preview {
      font-size: 14px;
      color: #666;
      line-height: 1.6;
      margin-bottom: 12px;
    }

    .card-info {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 12px;

      .info-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: #999;
      }
    }

    .card-footer {
      display: flex;
      gap: 8px;
      padding-top: 12px;
      border-top: 1px solid #F0F0F0;

      .van-button {
        flex: 1;
        border-radius: 8px;
        font-size: 13px;
      }
    }
  }
}

// 弹窗样式
.dialog-content {
  height: 100%;
  display: flex;
  flex-direction: column;

  .dialog-header {
    padding: 16px;
    text-align: center;
    border-bottom: 1px solid #F0F0F0;

    .dialog-title {
      font-size: 18px;
      font-weight: bold;
      color: #333;
    }
  }

  .dialog-body {
    flex: 1;
    overflow-y: auto;
    padding: 16px 0;

    :deep(.van-cell-group--inset) {
      margin: 0 16px;
    }

    :deep(.van-field__label) {
      width: 70px;
      color: #333;
      font-weight: 500;
    }
  }

  .dialog-footer {
    padding: 16px;
    border-top: 1px solid #F0F0F0;

    .van-button {
      border-radius: 8px;
    }
  }
}

// 封面上传
.cover-upload {
  .cover-preview {
    position: relative;
    display: inline-block;

    .remove-icon {
      position: absolute;
      top: -8px;
      right: -8px;
      font-size: 18px;
      color: #EE0A24;
      background: #fff;
      border-radius: 50%;
    }
  }
}

// 过期时间字段
.expire-time-field {
  display: flex;
  align-items: center;
  gap: 8px;

  .expire-time-value {
    color: #333;
  }

  .expire-time-placeholder {
    color: #999;
  }

  .clear-icon {
    font-size: 16px;
    color: #999;
  }
}
</style>
