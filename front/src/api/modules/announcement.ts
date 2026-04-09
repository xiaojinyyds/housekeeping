import request from '../index'

export default {
  // 公开接口 - 获取公告列表
  getList(params?: { page?: number; page_size?: number; type?: string }) {
    return request.get('/api/v1/announcement/list', { params })
  },

  // 公开接口 - 获取公告详情
  getDetail(id: string) {
    return request.get(`/api/v1/announcement/detail/${id}`)
  },

  // 管理员接口 - 获取公告列表
  adminGetList(params?: {
    page?: number
    page_size?: number
    type?: string
    is_published?: boolean
    keyword?: string
  }) {
    return request.get('/api/v1/announcement/admin/list', { params })
  },

  // 管理员接口 - 创建公告
  create(data: {
    title: string
    content: string
    cover_image?: string
    type?: string
    is_published?: boolean
    expire_time?: string
    is_top?: boolean
  }) {
    return request.post('/api/v1/announcement/admin/create', data)
  },

  // 管理员接口 - 更新公告
  update(id: string, data: {
    title?: string
    content?: string
    cover_image?: string
    type?: string
    is_published?: boolean
    expire_time?: string
    is_top?: boolean
  }) {
    return request.put(`/api/v1/announcement/admin/${id}`, data)
  },

  // 管理员接口 - 删除公告
  delete(id: string) {
    return request.delete(`/api/v1/announcement/admin/${id}`)
  },

  // 管理员接口 - 发布公告
  publish(id: string) {
    return request.post(`/api/v1/announcement/admin/${id}/publish`)
  },

  // 管理员接口 - 取消发布
  unpublish(id: string) {
    return request.post(`/api/v1/announcement/admin/${id}/unpublish`)
  },
}
