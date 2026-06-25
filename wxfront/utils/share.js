/**
 * 微信小程序真实分享配置（转发好友 / 朋友圈）
 */
const MOCK_WORKER_ID = "mock-worker-user-1";
const DEFAULT_SHARE_IMAGE = "";

const ensureHttps = (url) => {
  if (!url || typeof url !== "string") return "";
  const trimmed = url.trim();
  if (!trimmed) return "";
  return trimmed.startsWith("http://") ? trimmed.replace("http://", "https://") : trimmed;
};

const isMockWorkerId = (workerId) => {
  return !workerId || String(workerId).indexOf("mock") >= 0;
};

const buildWorkerQuery = (workerId, shareStaffId, from) => {
  const params = [`id=${encodeURIComponent(workerId)}`];
  if (shareStaffId) {
    params.push(`staff_id=${encodeURIComponent(shareStaffId)}`);
  }
  if (from) {
    params.push(`from=${encodeURIComponent(from)}`);
  }
  return params.join("&");
};

const buildWorkerSharePath = (workerId, shareStaffId, from = "share_app_message") => {
  if (isMockWorkerId(workerId)) return "";
  return `/pages/detail/index?${buildWorkerQuery(workerId, shareStaffId, from)}`;
};

const buildWorkerShareTitle = (worker) => {
  if (!worker) return "玉心家政 · 精选阿姨推荐";
  const name = worker.display_name || "阿姨";
  const jobs = worker.jobTypesText
    || (Array.isArray(worker.job_types) ? worker.job_types.slice(0, 2).join("·") : "");
  const exp = worker.experience_years ? `${worker.experience_years}年经验` : "";
  const parts = [name, jobs, exp].filter(Boolean);
  return parts.length ? parts.join(" | ") : `${name} · 玉心家政`;
};

const resolveShareImage = (worker) => {
  const url = ensureHttps(worker && worker.avatar_url);
  if (!url) return DEFAULT_SHARE_IMAGE;
  // 微信默认占位图不适合作为分享封面
  if (url.indexOf("mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0") >= 0) {
    return DEFAULT_SHARE_IMAGE;
  }
  return url;
};

const buildWorkerAppMessage = (worker, workerId, shareStaffId) => {
  const path = buildWorkerSharePath(workerId, shareStaffId, "share_app_message");
  const payload = {
    title: buildWorkerShareTitle(worker),
    path: path || "/pages/index/index"
  };
  const imageUrl = resolveShareImage(worker);
  if (imageUrl) payload.imageUrl = imageUrl;
  return payload;
};

const buildWorkerTimeline = (worker, workerId, shareStaffId) => {
  const query = isMockWorkerId(workerId)
    ? "from=share_timeline"
    : buildWorkerQuery(workerId, shareStaffId, "share_timeline");
  const payload = {
    title: buildWorkerShareTitle(worker),
    query
  };
  const imageUrl = resolveShareImage(worker);
  if (imageUrl) payload.imageUrl = imageUrl;
  return payload;
};

const buildHomeShare = () => ({
  title: "玉心家政 · 找阿姨",
  path: "/pages/index/index?from=share_app_message"
});

const buildHomeTimeline = () => ({
  title: "玉心家政 · 找阿姨",
  query: "from=share_timeline"
});

const wrapShareWithImageCheck = (config) => {
  if (!config.imageUrl || !wx.getImageInfo) {
    return config;
  }
  return {
    ...config,
    promise: new Promise((resolve) => {
      wx.getImageInfo({
        src: config.imageUrl,
        success: () => resolve(config),
        fail: () => {
          const next = Object.assign({}, config);
          delete next.imageUrl;
          resolve(next);
        }
      });
    })
  };
};

module.exports = {
  MOCK_WORKER_ID,
  isMockWorkerId,
  buildWorkerSharePath,
  buildWorkerAppMessage,
  buildWorkerTimeline,
  buildHomeShare,
  buildHomeTimeline,
  wrapShareWithImageCheck
};
