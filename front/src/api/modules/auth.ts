import api from '../index'

export default {
  // 发送验证码
  sendCode: (data: { email: string }) => api.post('/api/v1/auth/send-code', data),

  // 用户注册
  register: (data: {
    email: string
    password: string
    code: string
    nickname?: string
  }) => api.post('/api/v1/auth/register', data),

  // 用户登录
  login: (data: {
    account: string
    password: string
  }) => api.post('/api/v1/auth/login', data),

  // 获取当前用户信息
  getUserInfo: () => api.get('/api/v1/auth/me'),

  // 更新用户信息
  updateProfile: (data: {
    nickname?: string
    phone?: string
    avatar_url?: string
  }) => api.put('/api/v1/auth/update-profile', data),

  // 修改密码
  changePassword: (data: {
    old_password: string
    new_password: string
  }) => api.post('/api/v1/auth/change-password', data),

  // 忘记密码 - 发送验证码
  forgotPassword: (data: { email: string }) => api.post('/api/v1/auth/forgot-password', data),

  // 重置密码
  resetPassword: (data: {
    email: string
    code: string
    password: string
  }) => api.post('/api/v1/auth/reset-password', data),
}
