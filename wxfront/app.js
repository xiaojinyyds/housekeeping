// app.js
App({
  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    // 登录
    wx.login({
      success: res => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
      }
    })

    // 隐私政策检查
    this.checkPrivacyAgreement()
  },

  checkPrivacyAgreement() {
    const agreed = wx.getStorageSync('privacyAgreed')
    // 将是否需要显示隐私弹窗的标志存入全局数据
    // 首页将读取该标志并展示自定义弹窗（支持可点击链接）
    this.globalData.showPrivacyModal = !agreed
  },

  globalData: {
    userInfo: null,
    devApiBase: 'http://backend.langhuajing.cn/api/v1',
    lanApiBase: 'https://backend.langhuajing.cn/api/v1'
  }
})
