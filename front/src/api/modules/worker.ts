import api from '../index'

export default {
  // 提交家政阿姨申请
  applyWorker: (data: {
    real_name: string
    id_card: string
    age: number
    gender: string
    address: string
    phone: string
    experience_years: number
    skills: string[]
    introduction: string
    id_card_front: string
    id_card_back: string
    health_certificate: string
    health_report: string
    practice_certificate: string
    other_certificates?: string[]
  }) => api.post('/api/v1/worker/apply', data),

  // 查看我的申请
  getMyApplication: () => api.get('/api/v1/worker/my-application'),

  // 更新申请信息
  updateApplication: (id: string, data: any) => api.put(`/api/v1/worker/application/${id}`, data),

  // 获取申请列表（管理员）
  getApplications: (params: {
    status?: string
    page?: number
    page_size?: number
  }) => api.get('/api/v1/worker/applications', { params }),

  // 审核申请（管理员）
  reviewApplication: (id: string, data: {
    status: string
    reject_reason?: string
  }) => api.post(`/api/v1/worker/applications/${id}/review`, data),

  // 获取我的家政阿姨档案
  getMyProfile: () => api.get('/api/v1/worker/profile'),

  // 更新我的档案（扩展版）
  updateMyProfile: (data: {
    phone?: string
    address?: string
    skills?: string[]
    introduction?: string
    service_areas?: string[]
    hourly_rate?: number
    is_available?: boolean
  }) => api.put('/api/v1/worker/profile', data),

  // 获取家政阿姨列表
  getWorkers: (params: {
    page?: number
    page_size?: number
    is_available?: boolean
    is_recommended?: boolean
    skills?: string
    city?: string  // 城市筛选
  }) => api.get('/api/v1/worker/workers', { params }),

  // 获取家政阿姨详情
  getWorkerDetail: (id: string) => api.get(`/api/v1/worker/workers/${id}`),

  // 获取阿姨排班表
  getWorkerSchedule: (id: string) => api.get(`/api/v1/worker/workers/${id}/schedule`),

  // ============ 时间段管理 ============

  // 获取所有可用时间段
  getTimeSlots: () => api.get('/api/v1/worker/time-slots'),

  // 获取我的可预约时间段
  getMySchedule: () => api.get('/api/v1/worker/schedule'),

  // 设置我的可预约时间段
  updateMySchedule: (data: {
    slots: Array<{
      day_of_week: number
      time_slot_id: string
      is_available: boolean
    }>
  }) => api.put('/api/v1/worker/schedule', data),

  // ============ 服务定价管理 ============

  // 获取所有服务项目
  getAllServices: () => api.get('/api/v1/worker/all-services'),

  // 获取我提供的服务
  getMyServices: () => api.get('/api/v1/worker/my-services'),

  // 添加/更新我的服务
  addMyService: (data: {
    service_id: string
    price: number
    is_active?: boolean
  }) => api.post('/api/v1/worker/my-services', data),

  // 移除我的服务
  removeMyService: (serviceId: string) => api.delete(`/api/v1/worker/my-services/${serviceId}`),

  // 获取阿姨收到评价
  getWorkerReviews: (workerId: string, params: {
    page?: number
    page_size?: number
  }) => api.get(`/api/v1/worker/workers/${workerId}/reviews`, { params }),
}

