// 1. 确保这里是 https
const DEFAULT_BASE_URL = "https://backend.langhuajing.cn/api/v1";
let hasLoggedBaseUrl = false;
const TOAST_MAX_LEN = 20;

const shortenToastText = (text) => {
  const value = String(text || "").trim();
  if (!value) return "请求失败";
  return value.length > TOAST_MAX_LEN ? `${value.slice(0, TOAST_MAX_LEN - 1)}…` : value;
};

const buildErrorText = (err) => {
  const raw = String((err && err.errMsg) || err || "").toLowerCase();
  if (raw.includes("url not in domain list")) return "域名未在小程序白名单(需HTTPS)";
  if (raw.includes("ssl") || raw.includes("tls")) return "SSL/TLS 证书验证失败";
  if (raw.includes("timeout")) return "请求超时";
  if (raw.includes("fail")) return "网络连接失败";
  return String((err && err.errMsg) || err || "请求失败");
};

const toQueryString = (params) => {
  const entries = Object.keys(params || {})
    .filter((key) => params[key] !== undefined && params[key] !== null && params[key] !== "")
    .map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`);
  return entries.length ? `?${entries.join("&")}` : "";
};

const request = (url, method = "GET", data = {}) => {
  return new Promise((resolve, reject) => {
    let baseUrl = DEFAULT_BASE_URL;
    
    try {
      const app = getApp();
      const systemInfo = wx.getSystemInfoSync();
      // 只有在开发者工具里才允许覆盖地址，防止手机端读取到错误的 lanApiBase
      if (systemInfo.platform === "devtools" && app.globalData && app.globalData.devApiBase) {
        baseUrl = app.globalData.devApiBase;
      }
    } catch (err) {}

    // 【核心修复】：强制纠正协议
    // 微信小程序线上/体验环境必须使用 https。如果由于某种原因变成了 http，在此强行修复。
    if (baseUrl.startsWith("http://")) {
      baseUrl = baseUrl.replace("http://", "https://");
    }

    if (!hasLoggedBaseUrl) {
      hasLoggedBaseUrl = true;
      console.log("[api] Final Base URL =", baseUrl);
    }

    wx.showNavigationBarLoading();
    wx.request({
      url: baseUrl + url,
      method,
      data,
      timeout: 20000,
      header: {
        "content-type": "application/json"
      },
      success: (res) => {
        // 兼容处理：有些后端返回 code 200，有些只看 statusCode 200
        if (res.statusCode === 200 && (res.data.code === 200 || res.data.success || !res.data.code)) {
          resolve(res.data.data || res.data);
          return;
        }

        const message = (res && res.data && (res.data.message || res.data.detail || res.data.msg)) || `HTTP ${res.statusCode}`;
        console.warn("API Error:", res.statusCode, res.data, "url=", baseUrl + url);
        wx.showToast({ title: shortenToastText(message), icon: "none", duration: 2500 });
        reject(res.data);
      },
      fail: (err) => {
        const text = buildErrorText(err);
        console.error("Request Fail:", err, "url=", baseUrl + url);
        wx.showToast({ title: shortenToastText(text), icon: "none", duration: 3000 });
        reject({ message: text, raw: err });
      },
      complete: () => {
        wx.hideNavigationBarLoading();
      }
    });
  });
};

module.exports = {
  getWorkers: (page = 1, pageSize = 10, filters = {}) => {
    const query = toQueryString({
      page,
      page_size: pageSize,
      is_available: filters.is_available,
      is_recommended: filters.is_recommended,
      keyword: filters.keyword,
      job_type: filters.job_type,
      service_area: filters.service_area
    });
    return request(`/worker/workers${query}`, "GET");
  },
  getWorkerDetail: (id) => {
    return request(`/worker/workers/${id}`, "GET");
  },
  submitLead: (data) => {
    return request("/appointment/guest-leads", "POST", data);
  }
};