import apiAuth from '@/api/modules/auth'
import router from '@/router'

export const useUserStore = defineStore(
  // 唯一ID
  'user',
  () => {
    const userInfo = ref<any>(null)
    const token = ref(localStorage.token ?? '')

    const isLogin = computed(() => {
      return !!token.value
    })

    const userRole = computed(() => {
      return userInfo.value?.role || 'user'
    })

    const isWorker = computed(() => {
      return userInfo.value?.role === 'worker'
    })

    const isAdmin = computed(() => {
      return userInfo.value?.role === 'admin'
    })

    // 获取默认头像
    const defaultAvatar = computed(() => {
      if (userInfo.value?.role === 'admin') {
        return new URL('@/assets/images/管理员.png', import.meta.url).href
      }
      else if (userInfo.value?.role === 'worker') {
        return new URL('@/assets/images/阿姨.png', import.meta.url).href
      }
      else {
        return new URL('@/assets/images/用户.png', import.meta.url).href
      }
    })

    // 获取用户头像（优先使用自定义头像，否则使用默认头像）
    const userAvatar = computed(() => {
      return userInfo.value?.avatar_url || defaultAvatar.value
    })

    // 登录
    function login(data: {
      account: string
      password: string
    }) {
      return new Promise((resolve, reject) => {
        apiAuth.login(data).then((res) => {
          if (res.code === 200) {
            token.value = res.data.access_token
            userInfo.value = res.data.user
            localStorage.setItem('token', res.data.access_token)
            localStorage.setItem('userInfo', JSON.stringify(res.data.user))
            resolve(res)
          }
          else {
            reject(res)
          }
        }).catch((error) => {
          reject(error)
        })
      })
    }

    // 注册
    function register(data: {
      email: string
      password: string
      code: string
      nickname?: string
    }) {
      return new Promise((resolve, reject) => {
        apiAuth.register(data).then((res) => {
          if (res.code === 200) {
            token.value = res.data.access_token
            userInfo.value = res.data.user
            localStorage.setItem('token', res.data.access_token)
            localStorage.setItem('userInfo', JSON.stringify(res.data.user))
            resolve(res)
          }
          else {
            reject(res)
          }
        }).catch((error) => {
          reject(error)
        })
      })
    }

    // 退出登录
    function logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      token.value = ''
      userInfo.value = null
      router.push('/login')
    }

    // 获取用户信息
    async function getUserInfo() {
      try {
        const res = await apiAuth.getUserInfo()
        if (res.code === 200) {
          userInfo.value = res.data
          localStorage.setItem('userInfo', JSON.stringify(res.data))
          return res.data
        }
      }
      catch (error) {
        console.error('获取用户信息失败:', error)
        logout()
      }
    }

    // 更新用户信息
    async function updateUserInfo(data: any) {
      try {
        const res = await apiAuth.updateProfile(data)
        if (res.code === 200) {
          userInfo.value = { ...userInfo.value, ...res.data }
          localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
          return res.data
        }
      }
      catch (error) {
        console.error('更新用户信息失败:', error)
        throw error
      }
    }

    // 初始化用户信息（从localStorage恢复）
    function initUserInfo() {
      const savedUserInfo = localStorage.getItem('userInfo')
      if (savedUserInfo) {
        try {
          userInfo.value = JSON.parse(savedUserInfo)
        }
        catch (e) {
          console.error('解析用户信息失败:', e)
        }
      }
    }

    // 初始化
    initUserInfo()

    return {
      userInfo,
      token,
      isLogin,
      userRole,
      isWorker,
      isAdmin,
      defaultAvatar,
      userAvatar,
      login,
      register,
      logout,
      getUserInfo,
      updateUserInfo,
    }
  },
)
