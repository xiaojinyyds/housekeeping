<script setup lang="ts">
import { showToast } from 'vant'
import apiAuth from '@/api/modules/auth'

definePage({
  name: 'register',
  meta: {
    title: '注册',
  },
})

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)

// 表单数据
const formData = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: '',
  nickname: '',
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
  { required: true, message: '请输入密码' },
  { min: 6, message: '密码至少6位' },
]

const confirmPasswordRules = [
  { required: true, message: '请再次输入密码' },
  {
    validator: (val: string) => val === formData.password,
    message: '两次密码输入不一致',
  },
]

// 发送验证码
async function sendCode() {
  if (!formData.email) {
    showToast('请先输入邮箱')
    return
  }
  if (!/^[\w.-]+@[\w.-]+\.\w+$/.test(formData.email)) {
    showToast('请输入正确的邮箱格式')
    return
  }

  sendingCode.value = true
  try {
    const res = await apiAuth.sendCode({ email: formData.email })
    if (res.code === 200) {
      showToast({ message: '验证码已发送', icon: 'success' })
      countdown.value = 60
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    }
  }
  catch (error: any) {
    showToast({ message: error.message || '发送失败', icon: 'fail' })
  }
  finally {
    sendingCode.value = false
  }
}

// 注册
async function handleRegister() {
  loading.value = true
  try {
    await userStore.register({
      email: formData.email,
      code: formData.code,
      password: formData.password,
      nickname: formData.nickname || undefined,
    })
    showToast({ message: '注册成功', icon: 'success' })
    setTimeout(() => {
      router.replace('/')
    }, 500)
  }
  catch (error: any) {
    showToast({ message: error.message || '注册失败', icon: 'fail' })
  }
  finally {
    loading.value = false
  }
}

// 返回登录
function goLogin() {
  router.back()
}
</script>

<template>
  <div class="register-page">
    <!-- 头部区域 -->
    <div class="header-section">
      <div class="brand-content">
        <h1 class="brand-title">加入我们</h1>
        <p class="brand-slogan">开启温馨家政服务之旅</p>
      </div>
    </div>

    <!-- 表单卡片区域 -->
    <div class="form-card">
      <div class="card-header">
        <h2 class="form-title">创建账号</h2>
        <p class="form-subtitle">填写信息，快速注册</p>
      </div>

      <van-form @submit="handleRegister">
        <div class="form-fields">
          <van-field
            v-model="formData.email"
            name="email"
            type="email"
            placeholder="请输入邮箱"
            :rules="emailRules"
            left-icon="envelop-o"
            clearable
            class="custom-field"
          />

          <div class="code-field-wrapper">
            <van-field
              v-model="formData.code"
              name="code"
              type="digit"
              maxlength="6"
              placeholder="请输入6位验证码"
              :rules="codeRules"
              left-icon="shield-o"
              clearable
              class="custom-field code-input"
            />
            <van-button
              size="small"
              type="primary"
              :disabled="countdown > 0 || sendingCode"
              :loading="sendingCode"
              class="code-button"
              @click="sendCode"
            >
              {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
            </van-button>
          </div>

          <van-field
            v-model="formData.nickname"
            name="nickname"
            placeholder="请输入昵称（可选）"
            left-icon="user-o"
            clearable
            class="custom-field"
          />
          
          <van-field
            v-model="formData.password"
            type="password"
            name="password"
            placeholder="请输入密码（至少6位）"
            :rules="passwordRules"
            left-icon="lock"
            clearable
            class="custom-field"
          />

          <van-field
            v-model="formData.confirmPassword"
            type="password"
            name="confirmPassword"
            placeholder="请再次输入密码"
            :rules="confirmPasswordRules"
            left-icon="lock"
            clearable
            class="custom-field"
          />
        </div>

        <div class="form-actions">
          <van-button
            round
            block
            type="primary"
            native-type="submit"
            :loading="loading"
            loading-text="注册中..."
            class="submit-button"
          >
            <span class="button-text">立即注册</span>
          </van-button>

          <div class="login-tip">
            <span class="tip-text">已有账号？</span>
            <span class="link-text" @click="goLogin">立即登录</span>
          </div>
        </div>
      </van-form>
    </div>

    <!-- 底部装饰 -->
    <div class="footer-decoration">
      <div class="decoration-circle circle-1" />
      <div class="decoration-circle circle-2" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.register-page {
  min-height: 100vh;
  background: #FDF6EC;
  position: relative;
  overflow-x: hidden;
  padding-bottom: 40px;
}

// 头部区域 - 35%
.header-section {
  position: relative;
  height: 35vh;
  min-height: 280px;
  background: linear-gradient(135deg, #FF9F43 0%, #FF7F50 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom-left-radius: 50% 8%;
  border-bottom-right-radius: 50% 8%;
  box-shadow: 0 4px 20px rgba(255, 127, 80, 0.3);

  .brand-content {
    position: relative;
    z-index: 2;
    text-align: center;
    padding: 20px;

    .brand-title {
      font-size: 36px;
      font-weight: bold;
      color: #fff;
      margin-bottom: 12px;
      text-shadow: 0 3px 15px rgba(0, 0, 0, 0.25);
      letter-spacing: 4px;
    }

    .brand-slogan {
      font-size: 17px;
      color: #fff;
      font-weight: 600;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
      letter-spacing: 1px;
    }
  }
}

// 表单卡片
.form-card {
  position: relative;
  margin: -50px 20px 0;
  background: #fff;
  border-radius: 24px;
  padding: 32px 24px;
  box-shadow: 0 10px 40px rgba(255, 127, 80, 0.2);
  z-index: 3;

  .card-header {
    text-align: center;
    margin-bottom: 28px;

    .form-title {
      font-size: 24px;
      font-weight: bold;
      color: #333;
      margin-bottom: 8px;
    }

    .form-subtitle {
      font-size: 14px;
      color: #999;
    }
  }

  .form-fields {
    margin-bottom: 24px;

    .custom-field {
      background: #F5F6FA;
      border-radius: 16px;
      margin-bottom: 14px;
      border: none;
      overflow: hidden;

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
        padding: 15px 18px;
        background: transparent;
      }

      &:focus-within {
        background: #EBEDF5;
        box-shadow: 0 0 0 2px rgba(255, 159, 67, 0.1);
      }
    }

    .code-field-wrapper {
      position: relative;
      margin-bottom: 14px;

      .code-input {
        padding-right: 110px;
      }

      .code-button {
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
        height: 36px;
        padding: 0 16px;
        background: linear-gradient(135deg, #FF9F43 0%, #FFAD60 100%);
        border: none;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 600;
        color: #fff;
        box-shadow: 0 2px 8px rgba(255, 159, 67, 0.25);

        &:active:not(:disabled) {
          opacity: 0.8;
        }

        &:disabled {
          background: #ddd;
          color: #999;
          box-shadow: none;
        }
      }
    }
  }

  .form-actions {
    .submit-button {
      height: 52px;
      background: linear-gradient(135deg, #FF9F43 0%, #FFAD60 100%);
      border: none;
      box-shadow: 0 6px 20px rgba(255, 159, 67, 0.35);
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

    .login-tip {
      text-align: center;
      font-size: 14px;

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
}

// 底部装饰
.footer-decoration {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 150px;
  pointer-events: none;
  z-index: 1;

  .decoration-circle {
    position: absolute;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 159, 67, 0.08) 0%, transparent 70%);
  }

  .circle-1 {
    width: 120px;
    height: 120px;
    bottom: -40px;
    right: -20px;
    animation: float-slow 7s ease-in-out infinite;
  }

  .circle-2 {
    width: 90px;
    height: 90px;
    bottom: 30px;
    left: 20px;
    animation: float-slow 9s ease-in-out infinite reverse;
  }
}

@keyframes float-slow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}
</style>
