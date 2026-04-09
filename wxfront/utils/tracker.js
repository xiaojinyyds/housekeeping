const STORAGE_KEY = 'wx_lead_success_track_logs';
const MAX_LOGS = 50;

const normalizeValue = (value) => {
  if (value === undefined || value === null) return '';
  return String(value).slice(0, 100);
};

const saveLocalLog = (eventName, payload) => {
  try {
    const history = wx.getStorageSync(STORAGE_KEY) || [];
    const next = [{
      event: eventName,
      payload: payload,
      timestamp: Date.now()
    }].concat(history).slice(0, MAX_LOGS);
    wx.setStorageSync(STORAGE_KEY, next);
  } catch (err) {
    console.warn('track local log failed', err);
  }
};

const reportAnalytics = (eventName, payload) => {
  if (!wx || typeof wx.reportAnalytics !== 'function') return;
  try {
    wx.reportAnalytics(eventName, payload);
  } catch (err) {
    console.warn('reportAnalytics failed', err);
  }
};

const trackEvent = (eventName, payload) => {
  const safePayload = {};
  Object.keys(payload || {}).forEach((key) => {
    safePayload[key] = normalizeValue(payload[key]);
  });
  reportAnalytics(eventName, safePayload);
  saveLocalLog(eventName, safePayload);
};

const trackLeadSuccess = (payload) => {
  trackEvent('lead_submit_success', payload || {});
};

module.exports = {
  trackLeadSuccess
};
