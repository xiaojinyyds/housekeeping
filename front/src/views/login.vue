<script setup lang="ts">
import { showToast } from 'vant'
import apiAuth from '@/api/modules/auth'

definePage({
  name: 'login',
  meta: {
    title: '登录',
  },
})

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const redirect = ref(route.query.redirect?.toString() ?? '/')
const loading = ref(false)

// 表单数据
const formData = reactive({
  account: '',
  password: '',
})

// 表单验证规则
const accountRules = [
  { required: true, message: '请输入邮箱或手机号' },
  { pattern: /^[\w.-]+@[\w.-]+\.\w+$|^1[3-9]\d{9}$/, message: '请输入正确的邮箱或手机号' },
]

const passwordRules = [
  { required: true, message: '请输入密码' },
  { min: 6, message: '密码至少6位' },
]

// 登录
async function handleLogin() {
  loading.value = true
  try {
    await userStore.login({
      account: formData.account,
      password: formData.password,
    })
    showToast({ message: '登录成功', icon: 'success' })
    setTimeout(() => {
      router.replace(redirect.value)
    }, 500)
  }
  catch (error: any) {
    showToast({ message: error.message || '登录失败', icon: 'fail' })
  }
  finally {
    loading.value = false
  }
}

// 跳转注册
function goRegister() {
  router.push('/register')
}

// 跳转忘记密码
function goForgotPassword() {
  router.push('/forgot-password')
}
</script>

<template>
  <div class="login-page">
    <!-- 头部区域 - 35% 高度 -->
    <div class="header-section">
      <div class="brand-content">
        <h1 class="brand-title">焕新你的家</h1>
        <p class="brand-slogan">专业家政 · 贴心服务</p>
      </div>
    </div>

    <!-- 表单卡片区域 -->
    <div class="form-card">
      <div class="card-header">
        <h2 class="form-title">欢迎回来</h2>
        <p class="form-subtitle">登录您的账号，开启美好生活</p>
      </div>

      <van-form @submit="handleLogin">
        <div class="form-fields">
          <van-field
            v-model="formData.account"
            name="account"
            placeholder="请输入邮箱或手机号"
            :rules="accountRules"
            left-icon="user-o"
            clearable
            class="custom-field"
          />
          
          <van-field
            v-model="formData.password"
            type="password"
            name="password"
            placeholder="请输入密码"
            :rules="passwordRules"
            left-icon="lock"
            clearable
            class="custom-field"
          />
        </div>

        <div class="form-actions">
          <div class="forgot-password-link">
            <span class="link-text" @click="goForgotPassword">忘记密码？</span>
          </div>

          <van-button
            round
            block
            type="primary"
            native-type="submit"
            :loading="loading"
            loading-text="登录中..."
            class="submit-button"
          >
            <span class="button-text">立即登录</span>
          </van-button>

          <div class="register-tip">
            <span class="tip-text">还没有账号？</span>
            <span class="link-text" @click="goRegister">立即注册</span>
          </div>
        </div>
      </van-form>
    </div>

    <!-- 底部装饰 -->
    <div class="footer-decoration">
      <div class="decoration-circle circle-1" />
      <div class="decoration-circle circle-2" />
      <div class="decoration-circle circle-3" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  background: #FDF6EC;
  position: relative;
  overflow: hidden;
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
      font-size: 38px;
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
    margin-bottom: 32px;

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
      margin-bottom: 16px;
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
        padding: 16px 20px;
        background: transparent;
      }

      &:focus-within {
        background: #EBEDF5;
        box-shadow: 0 0 0 2px rgba(255, 159, 67, 0.1);
      }
    }
  }

  .form-actions {
    .forgot-password-link {
      text-align: right;
      margin-bottom: 16px;

      .link-text {
        font-size: 13px;
        color: #FF9F43;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s;

        &:active {
          opacity: 0.7;
        }
      }
    }

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

    .register-tip {
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
  height: 200px;
  pointer-events: none;
  z-index: 1;

  .decoration-circle {
    position: absolute;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 159, 67, 0.08) 0%, transparent 70%);
  }

  .circle-1 {
    width: 150px;
    height: 150px;
    bottom: -50px;
    left: -30px;
    animation: float-slow 6s ease-in-out infinite;
  }

  .circle-2 {
    width: 100px;
    height: 100px;
    bottom: 20px;
    right: 40px;
    animation: float-slow 8s ease-in-out infinite reverse;
  }

  .circle-3 {
    width: 80px;
    height: 80px;
    bottom: 80px;
    left: 50%;
    animation: float-slow 7s ease-in-out infinite;
  }
}

@keyframes float-slow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}
</style>
