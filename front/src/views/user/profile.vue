<script setup lang="ts">
import { showToast, showLoadingToast, closeToast } from 'vant'
import apiAuth from '@/api/modules/auth'
import apiUpload from '@/api/modules/upload'

definePage({
  name: 'user-profile',
  meta: {
    title: '个人信息',
    auth: true,
  },
})

// 返回上一页
function goBack() {
  router.back()
}

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('info')
const loading = ref(false)
const uploading = ref(false)

// 密码可见性
const passwordVisible = ref({
  old: false,
  new: false,
  confirm: false,
})

// 个人信息表单
const profileForm = reactive({
  nickname: '',
  avatar_url: '',
})

// 修改密码表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

// 初始化表单数据
function initForm() {
  if (userStore.userInfo) {
    profileForm.nickname = userStore.userInfo.nickname || ''
    profileForm.avatar_url = userStore.userInfo.avatar_url || ''
  }
}

// 当前显示的头像
const currentAvatar = computed(() => {
  return profileForm.avatar_url || userStore.userAvatar
})

// 选择头像文件
async function selectAvatar() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  
  input.onchange = async (e: any) => {
    const file = e.target.files[0]
    if (!file) return
    
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      showToast('请上传图片文件')
      return
    }
    
    // 检查文件大小（限制5MB）
    if (file.size > 5 * 1024 * 1024) {
      showToast('图片大小不能超过5MB')
      return
    }
    
    await uploadAvatar(file)
  }
  
  input.click()
}

// 上传头像到OSS
async function uploadAvatar(file: File) {
  uploading.value = true
  const toast = showLoadingToast({
    message: '上传中...',
    forbidClick: true,
    duration: 0,
  })

  try {
    // 使用专门的头像上传接口
    const res = await apiUpload.uploadAvatar(file)
    
    if (res.code === 200) {
      profileForm.avatar_url = res.data.url
      showToast('上传成功')
    }
    else {
      throw new Error(res.message || '上传失败')
    }
  }
  catch (error: any) {
    showToast(error.message || '上传失败')
  }
  finally {
    uploading.value = false
    closeToast()
  }
}

// 保存个人信息
async function saveProfile() {
  if (!profileForm.nickname) {
    showToast('请输入昵称')
    return
  }

  loading.value = true
  try {
    await userStore.updateUserInfo({
      nickname: profileForm.nickname,
      avatar_url: profileForm.avatar_url,
    })
    showToast('保存成功')
    setTimeout(() => {
      router.back()
    }, 500)
  }
  catch (error: any) {
    showToast(error.message || '保存失败')
  }
  finally {
    loading.value = false
  }
}

// 修改密码
async function changePassword() {
  if (!passwordForm.old_password) {
    showToast('请输入原密码')
    return
  }
  if (!passwordForm.new_password) {
    showToast('请输入新密码')
    return
  }
  if (passwordForm.new_password.length < 6) {
    showToast('新密码至少6位')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    showToast('两次密码输入不一致')
    return
  }

  loading.value = true
  try {
    const res = await apiAuth.changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
    })
    
    if (res.code === 200) {
      showToast('修改成功，请重新登录')
      // 清空表单
      passwordForm.old_password = ''
      passwordForm.new_password = ''
      passwordForm.confirm_password = ''
      // 退出登录
      setTimeout(() => {
        userStore.logout()
      }, 1500)
    }
  }
  catch (error: any) {
    showToast(error.message || '修改失败')
  }
  finally {
    loading.value = false
  }
}

// 切换密码可见性
function togglePasswordVisible(field: 'old' | 'new' | 'confirm') {
  passwordVisible.value[field] = !passwordVisible.value[field]
}

onMounted(() => {
  initForm()
})
</script>

<template>
  <div class="profile-page">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      title="个人信息"
      left-arrow
      fixed
      placeholder
      @click-left="goBack"
    />

    <van-tabs
      v-model:active="activeTab"
      sticky
      color="#FF9F43"
      title-active-color="#FF9F43"
      title-inactive-color="#969799"
    >
      <!-- 修改信息 -->
      <van-tab title="修改信息" name="info">
        <div class="tab-content">
          <!-- 头像区域 -->
          <div class="avatar-section" @click="selectAvatar">
            <div class="avatar-wrapper">
              <van-image
                round
                width="80"
                height="80"
                :src="currentAvatar"
                fit="cover"
                class="avatar-image"
              />
              <div class="avatar-camera">
                <van-icon name="photograph" size="16" color="#fff" />
              </div>
              <van-loading v-if="uploading" class="avatar-loading" size="24" color="#FF9F43" />
            </div>
            <div class="avatar-tip">点击更换头像</div>
          </div>

          <!-- 信息列表 -->
          <van-cell-group inset class="info-group">
            <van-field
              v-model="profileForm.nickname"
              label="昵称"
              placeholder="请输入昵称"
              input-align="right"
              clearable
            />
            
            <van-cell
              title="邮箱"
              :value="userStore.userInfo?.email"
              value-class="cell-value-gray"
            />

            <van-cell title="角色">
              <template #value>
                <van-tag
                  v-if="userStore.isAdmin"
                  type="danger"
                  size="mini"
                >
                  管理员
                </van-tag>
                <van-tag
                  v-else-if="userStore.isWorker"
                  type="success"
                  size="mini"
                >
                  家政阿姨
                </van-tag>
                <van-tag
                  v-else
                  type="primary"
                  size="mini"
                >
                  普通用户
                </van-tag>
              </template>
            </van-cell>
          </van-cell-group>

          <!-- 保存按钮 -->
          <div class="save-button">
            <van-button
              round
              block
              type="primary"
              :loading="loading"
              color="linear-gradient(to right, #FF9F43, #FF7F50)"
              @click="saveProfile"
            >
              保存修改
            </van-button>
          </div>
        </div>
      </van-tab>

      <!-- 修改密码 -->
      <van-tab title="修改密码" name="password">
        <div class="tab-content">
          <van-cell-group inset class="password-group">
            <van-field
              v-model="passwordForm.old_password"
              :type="passwordVisible.old ? 'text' : 'password'"
              label="原密码"
              placeholder="请输入原密码"
              left-icon="lock"
              clearable
            >
              <template #right-icon>
                <van-icon
                  :name="passwordVisible.old ? 'eye-o' : 'closed-eye'"
                  @click="togglePasswordVisible('old')"
                />
              </template>
            </van-field>
            
            <van-field
              v-model="passwordForm.new_password"
              :type="passwordVisible.new ? 'text' : 'password'"
              label="新密码"
              placeholder="请输入新密码（至少6位）"
              left-icon="lock"
              clearable
            >
              <template #right-icon>
                <van-icon
                  :name="passwordVisible.new ? 'eye-o' : 'closed-eye'"
                  @click="togglePasswordVisible('new')"
                />
              </template>
            </van-field>

            <van-field
              v-model="passwordForm.confirm_password"
              :type="passwordVisible.confirm ? 'text' : 'password'"
              label="确认密码"
              placeholder="请再次输入新密码"
              left-icon="lock"
              clearable
            >
              <template #right-icon>
                <van-icon
                  :name="passwordVisible.confirm ? 'eye-o' : 'closed-eye'"
                  @click="togglePasswordVisible('confirm')"
                />
              </template>
            </van-field>
          </van-cell-group>

          <!-- 确认按钮 -->
          <div class="save-button">
            <van-button
              round
              block
              type="primary"
              :loading="loading"
              color="linear-gradient(to right, #FF9F43, #FF7F50)"
              @click="changePassword"
            >
              确认修改
            </van-button>
            
            <!-- 温馨提示 -->
            <div class="password-tip">
              修改密码后需要重新登录
            </div>
          </div>
        </div>
      </van-tab>
    </van-tabs>
  </div>
</template>

<style scoped lang="scss">
// 颜色变量
$primary-color: #FF9F43;
$bg-color: #F7F8FA;
$text-gray: #969799;
$text-dark: #323233;

.profile-page {
  min-height: 100vh;
  background: $bg-color;

  :deep(.van-nav-bar) {
    background: #fff;

    .van-nav-bar__title {
      color: $text-dark;
      font-weight: 600;
    }

    .van-icon {
      color: $text-dark;
    }
  }

  :deep(.van-tabs__nav) {
    background: #fff;
  }

  :deep(.van-tabs__line) {
    background: $primary-color;
  }
}

.tab-content {
  padding: 16px 0 24px;
}

// 头像区域
.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 0;
  cursor: pointer;

  .avatar-wrapper {
    position: relative;
    margin-bottom: 12px;

    .avatar-image {
      border: 3px solid #fff;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    }

    .avatar-camera {
      position: absolute;
      right: 0;
      bottom: 0;
      width: 28px;
      height: 28px;
      background: $primary-color;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2px solid #fff;
      box-shadow: 0 2px 8px rgba(255, 159, 67, 0.4);
    }

    .avatar-loading {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: rgba(255, 255, 255, 0.9);
      border-radius: 50%;
      padding: 8px;
    }
  }

  .avatar-tip {
    font-size: 13px;
    color: $text-gray;
  }
}

// 信息列表
.info-group,
.password-group {
  margin: 0 16px 24px;
  border-radius: 12px;
  overflow: hidden;

  :deep(.van-cell) {
    padding: 14px 16px;
    font-size: 15px;

    &::after {
      border-color: #F5F5F5;
    }

    .van-cell__title {
      color: $text-dark;
    }

    .van-cell__value {
      color: $text-dark;
    }

    .cell-value-gray {
      color: $text-gray;
    }
  }

  :deep(.van-field__label) {
    width: 80px;
    color: $text-dark;
  }

  :deep(.van-field__control) {
    text-align: right;
  }

  :deep(.van-field__left-icon) {
    color: $primary-color;
    margin-right: 8px;
  }

  :deep(.van-field__right-icon) {
    color: $text-gray;
    cursor: pointer;

    &:active {
      opacity: 0.7;
    }
  }
}

// 保存按钮
.save-button {
  padding: 0 16px;

  .van-button {
    height: 46px;
    font-size: 16px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(255, 159, 67, 0.3);

    &:active {
      transform: translateY(1px);
    }
  }

  .password-tip {
    margin-top: 16px;
    text-align: center;
    font-size: 12px;
    color: $text-gray;
    line-height: 1.5;
  }
}
</style>
