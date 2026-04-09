import api from '../index'

export default {
  // ========== 用户管理 ==========
  
  // 获取用户列表
  getUsers: (params: {
    page?: number
    page_size?: number
    role?: string
    status?: string
    keyword?: string
  }) => api.get('/api/v1/admin/users', { params }),

  // 获取用户详情
  getUserDetail: (userId: string) => api.get(`/api/v1/admin/users/${userId}`),

  // 修改用户状态
  updateUserStatus: (userId: string, newStatus: string) =>
    api.put(`/api/v1/admin/users/${userId}/status?new_status=${newStatus}`),

  // 创建用户
  createUser: (data: {
    email: string
    password: string
    nickname?: string
    phone?: string
    role?: string
  }) => api.post('/api/v1/admin/users/create', data),

  // 修改用户信息
  updateUserInfo: (userId: string, data: {
    nickname?: string
    phone?: string
    avatar_url?: string
    role?: string
  }) => api.put(`/api/v1/admin/users/${userId}/info`, data),

  // 重置用户密码
  resetUserPassword: (userId: string, newPassword: string) =>
    api.post(`/api/v1/admin/users/${userId}/reset-password`, { new_password: newPassword }),

  // 删除用户
  deleteUser: (userId: string) => api.delete(`/api/v1/admin/users/${userId}`),

  // ========== 阿姨管理 ==========
  
  // 获取阿姨列表
  getWorkers: (params: {
    page?: number
    page_size?: number
    is_available?: boolean
    keyword?: string
  }) => api.get('/api/v1/admin/workers/list', { params }),

  // 修改阿姨接单状态
  updateWorkerAvailable: (workerId: string, isAvailable: boolean) =>
    api.put(`/api/v1/admin/workers/${workerId}/available?is_available=${isAvailable}`),

  // 设置阿姨首页推荐
  updateWorkerRecommend: (workerId: string, isRecommended: boolean) =>
    api.put(`/api/v1/admin/workers/${workerId}/recommend?is_recommended=${isRecommended}`),

  // 创建阿姨档案
  createWorker: (data: {
    email: string
    password: string
    real_name: string
    phone: string
    id_card: string
    gender: string
    age: number
    address: string
    work_years: number
    skills: string | string[]
    introduction: string
    health_certificate_url: string
    id_card_front_url: string
    id_card_back_url: string
    other_certificates?: string
  }) => api.post('/api/v1/admin/workers/create', data),

  // ========== 数据统计 ==========
  
  // 获取统计数据
  getStatistics: () => api.get('/api/v1/admin/statistics'),

  // ========== 数据导入导出 ==========
  
  // 导出阿姨名单
  exportWorkers: (params?: { is_available?: boolean; is_recommended?: boolean }) =>
    api.get('/api/v1/admin/data/export/workers', { 
      params, 
      responseType: 'blob' 
    }),

  // 导出用户列表
  exportUsers: (params?: { role?: string; status?: string }) =>
    api.get('/api/v1/admin/data/export/users', { 
      params, 
      responseType: 'blob' 
    }),

  // 导出订单数据
  exportOrders: (params?: { status?: string; start_date?: string; end_date?: string }) =>
    api.get('/api/v1/admin/data/export/orders', { 
      params, 
      responseType: 'blob' 
    }),

  // 导出统计报告
  exportStatistics: () =>
    api.get('/api/v1/admin/data/export/statistics', { 
      responseType: 'blob' 
    }),

  // 下载阿姨导入模板
  downloadWorkerTemplate: () =>
    api.get('/api/v1/admin/data/import/template/workers', { 
      responseType: 'blob' 
    }),

  // 下载用户导入模板
  downloadUserTemplate: () =>
    api.get('/api/v1/admin/data/import/template/users', { 
      responseType: 'blob' 
    }),

  // 批量导入阿姨
  importWorkers: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/api/v1/admin/data/import/workers', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 批量导入用户
  importUsers: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/api/v1/admin/data/import/users', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
}
