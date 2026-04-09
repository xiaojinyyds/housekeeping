import api from '@/api'

export default {
    // ============ 用户端 ============

    // 创建预约
    createAppointment: (data: {
        worker_id: string
        service_id?: string
        service_name: string
        appointment_date: string
        time_slot_id?: string
        time_slot_name: string
        duration_hours: number
        unit_price: number
        address: string
        contact_name: string
        contact_phone: string
        remark?: string
    }) => api.post('/api/v1/appointment', data),

    // 获取我的订单列表
    getMyAppointments: (params: {
        status?: string
        role?: string
        page?: number
        page_size?: number
    }) => api.get('/api/v1/appointment', { params }),

    // 获取订单详情
    getAppointmentDetail: (id: string) => api.get(`/api/v1/appointment/${id}`),

    // 取消订单
    cancelAppointment: (id: string, data: { reason?: string }) =>
        api.put(`/api/v1/appointment/${id}/cancel`, data),

    // 提交评价
    createReview: (id: string, data: {
        rating: number
        content?: string
        images?: string[]
        tags?: string[]
        is_anonymous?: boolean
    }) => api.post(`/api/v1/appointment/${id}/review`, data),

    // ============ 阿姨端 ============

    // 获取阿姨接单列表
    getWorkerOrders: (params: {
        status?: string
        page?: number
        page_size?: number
    }) => api.get('/api/v1/appointment/worker/orders', { params }),

    // 接单
    acceptOrder: (id: string) => api.put(`/api/v1/appointment/${id}/accept`),

    // 拒绝接单
    rejectOrder: (id: string, data: { reason: string }) =>
        api.put(`/api/v1/appointment/${id}/reject`, data),

    // 开始服务
    startService: (id: string) => api.put(`/api/v1/appointment/${id}/start`),

    // 完成服务
    completeService: (id: string) => api.put(`/api/v1/appointment/${id}/complete`),
}
