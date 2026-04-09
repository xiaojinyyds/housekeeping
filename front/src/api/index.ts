import axios from 'axios'
// import qs from 'qs'
import { toast } from 'vue-sonner'

// 请求重试配置
const MAX_RETRY_COUNT = 3 // 最大重试次数
const RETRY_DELAY = 1000 // 重试延迟时间（毫秒）

// 扩展 AxiosRequestConfig 类型
declare module 'axios' {
  export interface AxiosRequestConfig {
    retry?: boolean
    retryCount?: number
  }
}

const api = axios.create({
  baseURL: (import.meta.env.DEV && import.meta.env.VITE_OPEN_PROXY) ? '/proxy/' : import.meta.env.VITE_APP_API_BASEURL,
  timeout: 1000 * 60,
  responseType: 'json',
})

api.interceptors.request.use(
  (request) => {
    // 全局拦截请求发送前提交的参数
    const userStore = useUserStore()
    // 设置请求头
    if (request.headers) {
      if (userStore.isLogin && userStore.token) {
        request.headers.Authorization = `Bearer ${userStore.token}`
      }
    }
    return request
  },
)

// 处理错误信息的函数
function handleError(error: any) {
  if (error.status === 401) {
    useUserStore().logout()
    throw error
  }
  let message = error.message
  if (message === 'Network Error') {
    message = '后端网络故障'
  }
  else if (message.includes('timeout')) {
    message = '接口请求超时'
  }
  else if (message.includes('Request failed with status code')) {
    message = `接口${message.substr(message.length - 3)}异常`
  }
  toast.error('Error', {
    description: message,
  })
  return Promise.reject(error)
}

api.interceptors.response.use(
  (response) => {
    /**
     * 全局拦截请求发送后返回的数据
     * 后端返回格式：{ code: 200, message: 'success', data: {} }
     * code 为 200 表示成功，401 表示未登录，其他表示错误
     */
    // 如果是 blob 类型（文件下载），直接返回
    if (response.config.responseType === 'blob') {
      return Promise.resolve(response)
    }
    
    if (response.data.code === 200) {
      return Promise.resolve(response.data)
    }
    else if (response.data.code === 401) {
      toast.error('未登录或登录已过期')
      useUserStore().logout()
      return Promise.reject(response.data)
    }
    else {
      toast.error(response.data.message || '请求失败')
      return Promise.reject(response.data)
    }
  },
  async (error) => {
    // 获取请求配置
    const config = error.config

    // 如果配置不存在或未启用重试，则直接处理错误
    if (!config || !config.retry) {
      return handleError(error)
    }

    // 设置重试次数
    config.retryCount = config.retryCount || 0

    // 判断是否超过重试次数
    if (config.retryCount >= MAX_RETRY_COUNT) {
      return handleError(error)
    }

    // 重试次数自增
    config.retryCount += 1

    // 延迟重试
    await new Promise(resolve => setTimeout(resolve, RETRY_DELAY))

    // 重新发起请求
    return api(config)
  },
)

export default api
