<script setup lang="ts">
import { showToast } from 'vant'
import apiAuth from '@/api/modules/auth'

definePage({
  name: 'forgot-password',
  meta: {
    title: '忘记密码',
  },
})

const router = useRouter()

// 当前步骤：1-输入邮箱，2-输入验证码和新密码
const step = ref(1)
const loading = ref(false)
const countdown = ref(0)
let timer: any = null

// 表单数据
const formData = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: '',
})

// 表单验证规则
const emailRules = [
  { required: true, message: '请输入邮箱' },
  { pattern: /^[\w.-]+@[\w.-]+\.\w+$/, message: '请输入正确的邮箱格式' },
]

const codeRules = [
  { required: true, message: '请输入验证码' },
  { pattern: /^\d{6}$/, message: '验证码为6位数字' },
]

const passwordRules = [
  { required: true, message: '请输入新密码' },
  { min: 6, message: '密码至少6位' },
]

// 发送验证码
async function sendCode() {
  if (!formData.email) {
    showToast({ message: '请输入邮箱', icon: 'fail' })
    return
  }

  if (!/^[\w.-]+@[\w.-]+\.\w+$/.test(formData.email)) {
    showToast({ message: '请输入正确的邮箱格式', icon: 'fail' })
    return
  }

  if (countdown.value > 0) {
    return
  }

  loading.value = true
  try {
    await apiAuth.forgotPassword({ email: formData.email })
    showToast({ message: '验证码已发送', icon: 'success' })
    
    // 开始倒计时
    countdown.value = 60
    timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)

    // 进入下一步
    step.value = 2
  }
  catch (error: any) {
    showToast({ message: error.message || '发送失败', icon: 'fail' })
  }
  finally {
    loading.value = false
  }
}

// 重置密码
async function handleReset() {
  if (!formData.code) {
    showToast({ message: '请输入验证码', icon: 'fail' })
    return
  }

  if (!formData.password) {
    showToast({ message: '请输入新密码', icon: 'fail' })
    return
  }

  if (formData.password.length < 6) {
    showToast({ message: '密码至少6位', icon: 'fail' })
    return
  }

  if (formData.password !== formData.confirmPassword) {
    showToast({ message: '两次密码输入不一致', icon: 'fail' })
    return
  }

  loading.value = true
  try {
    await apiAuth.resetPassword({
      email: formData.email,
      code: formData.code,
      password: formData.password,
    })
    showToast({ message: '密码重置成功', icon: 'success' })
    setTimeout(() => {
      router.replace('/login')
    }, 1000)
  }
  catch (error: any) {
    showToast({ message: error.message || '重置失败', icon: 'fail' })
  }
  finally {
    loading.value = false
  }
}

// 返回上一步
function goBack() {
  if (step.value === 2) {
    step.value = 1
  }
  else {
    router.back()
  }
}

// 清理定时器
onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<template>
  <div class="forgot-password-page">
    <!-- 导航栏 -->
    <van-nav-bar
      title="忘记密码"
      left-arrow
      @click-left="goBack"
      class="custom-nav"
    />

    <!-- 头部区域 -->
    <div class="header-section">
      <div class="icon-wrapper">
        <van-icon name="lock" size="60" color="#FF9F43" />
      </div>
      <h2 class="header-title">重置密码</h2>
      <p class="header-subtitle">{{ step === 1 ? '请输入您的注册邮箱' : '请输入验证码和新密码' }}</p>
    </div>

    <!-- 表单区域 -->
    <div class="form-section">
      <!-- 步骤1：输入邮箱 -->
      <van-form v-if="step === 1" @submit="sendCode">
        <van-field
          v-model="formData.email"
          name="email"
          placeholder="请输入邮箱"
          :rules="emailRules"
          left-icon="envelop-o"
          clearable
          class="custom-field"
        />

        <van-button
          round
          block
          type="primary"
          native-type="submit"
          :loading="loading"
          loading-text="发送中..."
          class="submit-button"
        >
          <span class="button-text">发送验证码</span>
        </van-button>
      </van-form>

      <!-- 步骤2：输入验证码和新密码 -->
      <van-form v-else @submit="handleReset">
        <van-field
          v-model="formData.code"
          name="code"
          placeholder="请输入6位验证码"
          :rules="codeRules"
          left-icon="shield-o"
          maxlength="6"
          clearable
          class="custom-field"
        >
          <template #button>
            <van-button
              size="small"
              type="primary"
              plain
              :disabled="countdown > 0"
              @click="sendCode"
              class="code-button"
            >
              {{ countdown > 0 ? `${countdown}秒后重发` : '重新发送' }}
            </van-button>
          </template>
        </van-field>

        <van-field
          v-model="formData.password"
          type="password"
          name="password"
          placeholder="请输入新密码（至少6位）"
          :rules="passwordRules"
          left-icon="lock"
          clearable
          class="custom-field"
        />

        <van-field
          v-model="formData.confirmPassword"
          type="password"
          name="confirmPassword"
          placeholder="请再次输入新密码"
          :rules="passwordRules"
          left-icon="lock"
          clearable
          class="custom-field"
        />

        <van-button
          round
          block
          type="primary"
          native-type="submit"
          :loading="loading"
          loading-text="重置中..."
          class="submit-button"
        >
          <span class="button-text">确认重置</span>
        </van-button>
      </van-form>

      <!-- 返回登录 -->
      <div class="back-login">
        <span class="tip-text">想起密码了？</span>
        <span class="link-text" @click="router.push('/login')">返回登录</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.forgot-password-page {
  min-height: 100vh;
  background: #FDF6EC;
}

.custom-nav {
  background: linear-gradient(135deg, #FF9F43 0%, #FF7F50 100%);

  :deep(.van-nav-bar__title) {
    color: #fff;
    font-weight: 600;
  }

  :deep(.van-icon) {
    color: #fff;
  }
}

.header-section {
  padding: 40px 20px;
  text-align: center;

  .icon-wrapper {
    width: 100px;
    height: 100px;
    margin: 0 auto 20px;
    background: linear-gradient(135deg, #FFF5E6 0%, #FFE8CC 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 24px rgba(255, 159, 67, 0.2);
  }

  .header-title {
    font-size: 26px;
    font-weight: bold;
    color: #333;
    margin-bottom: 8px;
  }

  .header-subtitle {
    font-size: 14px;
    color: #999;
  }
}

.form-section {
  padding: 0 20px;

  .custom-field {
    background: #fff;
    border-radius: 16px;
    margin-bottom: 16px;
    border: none;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

    :deep(.van-field__control) {
      font-size: 15px;
      color: #333;
    }

    :deep(.van-field__left-icon) {
      color: #FF9F43;
      font-size: 20px;
      margin-right: 12px;
    }

    :deep(.van-cell) {
      padding: 16px 20px;
      background: transparent;
    }

    &:focus-within {
      box-shadow: 0 0 0 2px rgba(255, 159, 67, 0.1);
    }
  }

  .code-button {
    border-color: #FF9F43;
    color: #FF9F43;
    font-size: 13px;
    padding: 0 12px;
    height: 32px;

    &:disabled {
      opacity: 0.5;
    }
  }

  .submit-button {
    height: 52px;
    background: linear-gradient(135deg, #FF9F43 0%, #FFAD60 100%);
    border: none;
    box-shadow: 0 6px 20px rgba(255, 159, 67, 0.35);
    margin-top: 8px;
    margin-bottom: 20px;

    .button-text {
      font-size: 17px;
      font-weight: 600;
      letter-spacing: 1px;
    }

    &:active {
      transform: translateY(2px);
      box-shadow: 0 4px 12px rgba(255, 159, 67, 0.3);
    }
  }

  .back-login {
    text-align: center;
    font-size: 14px;
    padding: 20px 0;

    .tip-text {
      color: #999;
    }

    .link-text {
      color: #FF9F43;
      font-weight: 600;
      margin-left: 4px;
      cursor: pointer;
      transition: all 0.3s;

      &:active {
        opacity: 0.7;
      }
    }
  }
}
</style>
