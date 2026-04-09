import api from '../index'

export default {
  // 上传单张图片
  uploadImage: (file: File, folder = 'housekeeping') => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/api/v1/upload/image?folder=${folder}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 上传头像
  uploadAvatar: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/api/v1/upload/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 批量上传图片
  uploadBatch: (files: File[], folder = 'housekeeping') => {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })
    return api.post(`/api/v1/upload/batch?folder=${folder}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 删除图片
  deleteImage: (key: string) => api.delete(`/api/v1/upload/image?key=${key}`),
}
