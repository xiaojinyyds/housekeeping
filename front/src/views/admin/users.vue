<script setup lang="ts">
import { showToast, showConfirmDialog } from 'vant'
import apiAdmin from '@/api/modules/admin'

definePage({
  name: 'admin-users',
  meta: {
    title: '用户管理',
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
const userList = ref<any[]>([])
const page = ref(1)
const pageSize = 10

// 筛选条件
const activeTab = ref('all')
const tabs = [
  { name: 'all', title: '全部' },
  { name: 'user', title: '普通用户' },
  { name: 'worker', title: '家政阿姨' },
  { name: 'admin', title: '管理员' },
]

// 搜索关键词
const searchKeyword = ref('')

// 获取用户列表
async function getUsers(isRefresh = false) {
  if (isRefresh) {
    page.value = 1
    userList.value = []
    finished.value = false
  }

  loading.value = true
  try {
    const params: any = {
      page: page.value,
      page_size: pageSize,
    }

    if (activeTab.value !== 'all') {
      params.role = activeTab.value
    }

    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }

    const res: any = await apiAdmin.getUsers(params)

    if (res.code === 200) {
      if (isRefresh) {
        userList.value = res.data.list
      }
      else {
        userList.value.push(...res.data.list)
      }

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

// 切换标签
function onTabChange() {
  getUsers(true)
}

// 搜索
function onSearch() {
  getUsers(true)
}

// 下拉刷新
async function onRefresh() {
  await getUsers(true)
}

// 上拉加载
async function onLoad() {
  await getUsers()
}

// 切换用户状态
async function toggleUserStatus(user: any) {
  const newStatus = user.status === 'active' ? 'disabled' : 'active'
  const action = newStatus === 'active' ? '启用' : '禁用'

  try {
    await showConfirmDialog({
      title: `确认${action}`,
      message: `确定要${action}用户 ${user.nickname || user.email} 吗？`,
    })

    const res: any = await apiAdmin.updateUserStatus(user.id, newStatus)

    if (res.code === 200) {
      showToast(`${action}成功`)
      user.status = newStatus
    }
  }
  catch (error: any) {
    if (error !== 'cancel') {
      showToast(error.message || '操作失败')
    }
  }
}

// 角色标签颜色
function getRoleColor(role: string) {
  const colors: any = {
    user: '#1989FA',
    worker: '#07C160',
    admin: '#FF9F43',
  }
  return colors[role] || '#999'
}

// 角色文本
function getRoleText(role: string) {
  const texts: any = {
    user: '普通用户',
    worker: '家政阿姨',
    admin: '管理员',
  }
  return texts[role] || role
}

// ========== 创建/编辑用户 ==========
const showDialog = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const dialogTitle = computed(() => dialogMode.value === 'create' ? '创建用户' : '编辑用户')
const currentUser = ref<any>(null)

const dialogForm = reactive({
  email: '',
  password: '',
  nickname: '',
  phone: '',
  role: 'user',
})

const showRolePicker = ref(false)

// 打开创建对话框
function openCreateDialog() {
  dialogMode.value = 'create'
  dialogForm.email = ''
  dialogForm.password = ''
  dialogForm.nickname = ''
  dialogForm.phone = ''
  dialogForm.role = 'user'
  showDialog.value = true
}

// 打开编辑对话框
function openEditDialog(user: any) {
  dialogMode.value = 'edit'
  currentUser.value = user
  dialogForm.email = user.email
  dialogForm.password = ''
  dialogForm.nickname = user.nickname || ''
  dialogForm.phone = user.phone || ''
  dialogForm.role = user.role
  showDialog.value = true
}

// 提交表单
async function submitDialog() {
  if (!dialogForm.email) {
    showToast('请输入邮箱')
    return
  }

  if (dialogMode.value === 'create' && !dialogForm.password) {
    showToast('请输入密码')
    return
  }

  if (dialogMode.value === 'create' && dialogForm.password.length < 6) {
    showToast('密码至少6位')
    return
  }

  try {
    if (dialogMode.value === 'create') {
      // 创建用户
      const res: any = await apiAdmin.createUser({
        email: dialogForm.email,
        password: dialogForm.password,
        nickname: dialogForm.nickname || undefined,
        phone: dialogForm.phone || undefined,
        role: dialogForm.role,
      })

      if (res.code === 200) {
        showToast('创建成功')
        showDialog.value = false
        getUsers(true)
      }
    }
    else {
      // 编辑用户
      const res: any = await apiAdmin.updateUserInfo(currentUser.value.id, {
        nickname: dialogForm.nickname || undefined,
        phone: dialogForm.phone || undefined,
        role: dialogForm.role,
      })

      if (res.code === 200) {
        showToast('更新成功')
        showDialog.value = false
        getUsers(true)
      }
    }
  }
  catch (error: any) {
    showToast(error.message || '操作失败')
  }
}

// 重置密码
async function resetPassword(user: any) {
  try {
    await showConfirmDialog({
      title: '重置密码',
      message: '确定要重置该用户的密码为 123456 吗？',
    })

    const res: any = await apiAdmin.resetUserPassword(user.id, '123456')

    if (res.code === 200) {
      showToast('密码已重置为 123456')
    }
  }
  catch (error: any) {
    if (error !== 'cancel') {
      showToast(error.message || '操作失败')
    }
  }
}

// 删除用户
async function deleteUser(user: any) {
  try {
    await showConfirmDialog({
      title: '确认删除',
      message: `确定要删除用户 ${user.nickname || user.email} 吗？此操作不可恢复！`,
    })

    const res: any = await apiAdmin.deleteUser(user.id)

    if (res.code === 200) {
      showToast('删除成功')
      getUsers(true)
    }
  }
  catch (error: any) {
    if (error !== 'cancel') {
      showToast(error.message || '操作失败')
    }
  }
}

onMounted(() => {
  getUsers(true)
})
</script>

<template>
  <div class="admin-users-page">
    <van-nav-bar
      title="用户管理"
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
        placeholder="搜索邮箱/手机/昵称"
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
            <div class="user-list">
              <div
                v-for="user in userList"
                :key="user.id"
                class="user-card"
              >
                <!-- 卡片头部 -->
                <div class="card-header">
                  <!-- 左侧头像 -->
                  <div class="avatar-wrapper">
                    <van-image
                      v-if="user.avatar_url"
                      :src="user.avatar_url"
                      round
                      width="48"
                      height="48"
                      fit="cover"
                    />
                    <div v-else class="avatar">
                      {{ (user.nickname || user.email).charAt(0).toUpperCase() }}
                    </div>
                  </div>

                  <!-- 中间信息 -->
                  <div class="user-info">
                    <div class="user-name">
                      {{ user.nickname || user.email.split('@')[0] }}
                    </div>
                    <div class="user-meta">
                      <van-tag
                        plain
                        :color="getRoleColor(user.role)"
                      >
                        {{ getRoleText(user.role) }}
                      </van-tag>
                      <van-tag
                        v-if="user.status === 'disabled'"
                        plain
                        color="#EE0A24"
                        style="margin-left: 6px;"
                      >
                        已禁用
                      </van-tag>
                    </div>
                  </div>

                  <!-- 右侧开关 -->
                  <van-switch
                    :model-value="user.status === 'active'"
                    size="20"
                    @update:model-value="toggleUserStatus(user)"
                  />
                </div>

                <!-- 卡片内容 -->
                <div class="card-body">
                  <div class="info-item">
                    <van-icon name="envelop-o" size="14" color="#999" />
                    <span class="info-text">{{ user.email }}</span>
                  </div>
                  <div v-if="user.phone" class="info-item">
                    <van-icon name="phone-o" size="14" color="#999" />
                    <span class="info-text">{{ user.phone }}</span>
                  </div>
                  <div class="info-item">
                    <van-icon name="clock-o" size="14" color="#999" />
                    <span class="info-text">
                      注册于 {{ new Date(user.created_at).toLocaleDateString() }}
                    </span>
                  </div>
                  <div v-if="user.last_login_at" class="info-item">
                    <van-icon name="records" size="14" color="#999" />
                    <span class="info-text">
                      最后登录 {{ new Date(user.last_login_at).toLocaleString() }}
                    </span>
                  </div>
                </div>

                <!-- 卡片底部操作 -->
                <div class="card-footer">
                  <van-button
                    size="small"
                    plain
                    type="primary"
                    @click="openEditDialog(user)"
                  >
                    编辑
                  </van-button>
                  <van-button
                    size="small"
                    plain
                    type="warning"
                    @click="resetPassword(user)"
                  >
                    重置密码
                  </van-button>
                  <van-button
                    size="small"
                    plain
                    type="danger"
                    @click="deleteUser(user)"
                  >
                    删除
                  </van-button>
                </div>
              </div>
            </div>
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>

    <!-- 创建/编辑用户对话框 -->
    <van-dialog
      v-model:show="showDialog"
      :title="dialogTitle"
      show-cancel-button
      @confirm="submitDialog"
    >
      <div class="dialog-form">
        <van-field
          v-model="dialogForm.email"
          label="邮箱"
          placeholder="请输入邮箱"
          :disabled="dialogMode === 'edit'"
          required
        />
        <van-field
          v-if="dialogMode === 'create'"
          v-model="dialogForm.password"
          type="password"
          label="密码"
          placeholder="请输入密码（至少6位）"
          required
        />
        <van-field
          v-model="dialogForm.nickname"
          label="昵称"
          placeholder="请输入昵称（可选）"
        />
        <van-field
          v-model="dialogForm.phone"
          label="手机号"
          placeholder="请输入手机号（可选）"
        />
        <van-field
          v-model="dialogForm.role"
          label="角色"
          readonly
          clickable
          @click="showRolePicker = true"
        >
          <template #input>
            <span>{{ getRoleText(dialogForm.role) }}</span>
          </template>
        </van-field>
      </div>
    </van-dialog>

    <!-- 角色选择器 -->
    <van-popup v-model:show="showRolePicker" position="bottom">
      <van-picker
        :columns="[
          { text: '普通用户', value: 'user' },
          { text: '家政阿姨', value: 'worker' },
          { text: '管理员', value: 'admin' },
        ]"
        @confirm="(value: any) => { dialogForm.role = value.selectedOptions[0].value; showRolePicker = false }"
        @cancel="showRolePicker = false"
      />
    </van-popup>
  </div>
</template>

<style scoped lang="scss">
.admin-users-page {
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

// 搜索区域
.search-section {
  background: #fff;
  padding: 8px 0;

  :deep(.van-search) {
    padding: 8px 16px;
  }
}

// 用户列表
.user-list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;

  .user-card {
    background: #fff;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

    // 卡片头部
    .card-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;

      .avatar-wrapper {
        flex-shrink: 0;

        .avatar {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: linear-gradient(135deg, #1989FA 0%, #0E6FD8 100%);
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          font-weight: bold;
        }
      }

      .user-info {
        flex: 1;
        min-width: 0;

        .user-name {
          font-size: 16px;
          font-weight: bold;
          color: #333;
          margin-bottom: 6px;
        }

        .user-meta {
          display: flex;
          align-items: center;
        }
      }
    }

    // 卡片内容
    .card-body {
      .info-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        font-size: 13px;

        &:last-child {
          margin-bottom: 0;
        }

        .info-text {
          flex: 1;
          color: #666;
          line-height: 1.5;
        }
      }
    }
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

// 卡片底部操作
.card-footer {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #F0F0F0;

  .van-button {
    flex: 1;
    border-radius: 8px;
    font-size: 13px;
  }
}

// 对话框表单
.dialog-form {
  padding: 16px 0;

  :deep(.van-cell) {
    padding: 10px 16px;
  }

  :deep(.van-field__label) {
    width: 70px;
    color: #333;
    font-weight: 500;
  }
}
</style>
