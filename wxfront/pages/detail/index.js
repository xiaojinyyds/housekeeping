const api = require("../../utils/api.js");
const tracker = require("../../utils/tracker.js");
const share = require("../../utils/share.js");

const MOCK_WORKER_ID = "mock-worker-user-1";
const SERVICE_GUARANTEES = [
  "入职健康体检",
  "岗前严格背调",
  "服务保险保障",
  "无忧售后退换"
];

const MOCK_WORKER_DETAIL = {
  id: "mock-worker-profile-1",
  user_id: MOCK_WORKER_ID,
  display_name: "何**",
  age: 43,
  gender: "female",
  address: "浦东新区张江镇",
  zodiac: "猪",
  marital_status: "已婚",
  education: "高中",
  native_place: "四川南充",
  experience_years: 8,
  skills: ["做饭", "保洁", "带娃", "辅食添加"],
  job_types: ["白班育儿嫂", "白班保姆"],
  service_areas: ["浦东新区", "花木", "张江"],
  introduction: "家庭情况：三口之家经验充足\n性格描述：温和耐心\n性格爱好：喜欢孩子与烹饪\n擅长工作：小月龄照护、家常菜、家务整理",
  recommended_reasons: [
    "性格温和，沟通耐心",
    "带小月龄宝宝经验丰富",
    "会做宝宝辅食和家常菜"
  ],
  work_experiences: [
    {
      id: "mock-exp-1",
      start_date: "2021-03",
      end_date: "2023-08",
      company_name: "浦东三口之家",
      job_content: "负责1岁宝宝日常照护、辅食制作、玩教陪伴，并兼顾家庭卫生整理。"
    }
  ],
  life_photos: [],
  cert_badges: [
    { key: "real_name", label: "实名认证", verified: true },
    { key: "background", label: "背调认证", verified: true },
    { key: "health", label: "健康认证", verified: true },
    { key: "skill", label: "技能认证", verified: true }
  ],
  cert_images: [],
  service_guarantees: SERVICE_GUARANTEES,
  avatar_url: "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
  rating: 4.9,
  completed_orders: 126
};

function isDevtools() {
  try {
    const systemInfo = wx.getSystemInfoSync();
    return systemInfo && systemInfo.platform === "devtools";
  } catch (error) {
    return false;
  }
}

Page({
  data: {
    workerId: "",
    shareStaffId: "",
    worker: null,
    loading: true,
    showModal: false,
    showPrivacyModal: false,
    defaultAvatar: "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
    form: { name: "", phone: "", demand: "" }
  },

  onLoad(options) {
    this.enableShareMenus();
    const id = options && options.id;
    if (!id) {
      wx.showToast({ title: "参数错误", icon: "none" });
      setTimeout(() => wx.navigateBack(), 1200);
      return;
    }
    const staffId = (options && options.staff_id) || wx.getStorageSync("share_staff_id") || "";
    if (options && options.staff_id) {
      wx.setStorageSync("share_staff_id", options.staff_id);
    }
    this.setData({ workerId: id, shareStaffId: staffId });
    this.fetchDetail(id);
  },

  enableShareMenus() {
    if (!wx.showShareMenu) return;
    wx.showShareMenu({
      withShareTicket: true,
      menus: ["shareAppMessage", "shareTimeline"]
    });
  },

  getMockWorker() {
    return this.normalizeWorker(MOCK_WORKER_DETAIL);
  },

  fetchDetail(id) {
    if (isDevtools() && id === MOCK_WORKER_ID) {
      this.setData({ worker: this.getMockWorker(), loading: false });
      return;
    }

    this.setData({ loading: true });
    api.getWorkerDetail(id)
      .then((res) => {
        const worker = this.normalizeWorker(res || {});
        this.setData({ worker, loading: false });
      })
      .catch((err) => {
        console.error("fetch detail failed", err);
        if (isDevtools()) {
          this.setData({ worker: this.getMockWorker(), loading: false });
          return;
        }
        this.setData({ loading: false });
      });
  },

  normalizeWorker(res) {
    const worker = Object.assign({}, res);
    const skills = Array.isArray(worker.skills)
      ? worker.skills
      : (typeof worker.skills === "string" ? worker.skills.split(",") : []);

    worker.display_name = worker.display_name || (worker.real_name ? `${String(worker.real_name).slice(0, 1)}**` : "");
    worker.skillsArray = skills.filter(Boolean);
    worker.jobTypesText = Array.isArray(worker.job_types) ? worker.job_types.join(" / ") : "";
    worker.serviceAreasText = Array.isArray(worker.service_areas) ? worker.service_areas.join(" / ") : "";
    worker.certBadges = Array.isArray(worker.cert_badges) && worker.cert_badges.length
      ? worker.cert_badges
      : [
        { key: "real_name", label: "实名认证", verified: true },
        { key: "background", label: "背调认证", verified: true },
        { key: "health", label: "健康认证", verified: true },
        { key: "skill", label: "技能认证", verified: true }
      ];
    worker.certImages = Array.isArray(worker.cert_images) && worker.cert_images.length
      ? worker.cert_images
      : this.collectCertImages(worker);
    worker.lifePhotos = this.parsePhotoList(worker.life_photos).slice(0, 5);
    worker.recommendedReasons = Array.isArray(worker.recommended_reasons) ? worker.recommended_reasons : [];
    worker.workExperiences = Array.isArray(worker.work_experiences) ? worker.work_experiences : [];
    worker.serviceGuarantees = Array.isArray(worker.service_guarantees) && worker.service_guarantees.length
      ? worker.service_guarantees
      : SERVICE_GUARANTEES;
    worker.experience_years = worker.experience_years || 0;
    worker.rating = worker.rating || 5.0;
    worker.hasStructuredIntro = Boolean(
      worker.family_situation ||
      worker.personality_desc ||
      worker.personality_hobbies ||
      worker.skilled_work
    );
    return worker;
  },

  collectCertImages(worker) {
    const certImages = [];
    const add = (url, label) => {
      if (url) certImages.push({ url, label });
    };
    add(worker.health_certificate, "健康证");
    add(worker.health_report, "体检报告");
    add(worker.practice_certificate, "职业证书");
    if (Array.isArray(worker.other_certificates)) {
      worker.other_certificates.forEach((url, idx) => add(url, `其他证件${idx + 1}`));
    }
    return certImages;
  },

  parsePhotoList(value) {
    if (!value) return [];
    if (typeof value === "string") {
      const text = value.trim();
      if (!text) return [];
      if (text.startsWith("[")) {
        try {
          const parsed = JSON.parse(text);
          return Array.isArray(parsed) ? parsed.filter(Boolean) : [];
        } catch (error) {
          return [text];
        }
      }
      return [text];
    }
    return Array.isArray(value) ? value.filter(Boolean) : [];
  },

  previewAvatar() {
    const worker = this.data.worker || {};
    const url = worker.avatar_url || this.data.defaultAvatar;
    if (!url) return;
    wx.previewImage({ current: url, urls: [url] });
  },

  previewCert(e) {
    const url = e.currentTarget.dataset.url;
    const worker = this.data.worker || {};
    const urls = (worker.certImages || []).map((item) => item.url);
    wx.previewImage({ current: url, urls });
  },

  previewLifePhoto(e) {
    const url = e.currentTarget.dataset.url;
    const worker = this.data.worker || {};
    const urls = worker.lifePhotos || [];
    wx.previewImage({ current: url, urls });
  },

  onShareTap() {
    if (share.isMockWorkerId(this.data.workerId)) {
      wx.showToast({ title: "模拟数据无法分享，请使用真实阿姨", icon: "none" });
      return;
    }
  },

  onShareAppMessage() {
    if (share.isMockWorkerId(this.data.workerId)) {
      return share.buildHomeShare();
    }
    const config = share.buildWorkerAppMessage(
      this.data.worker,
      this.data.workerId,
      this.data.shareStaffId
    );
    return share.wrapShareWithImageCheck(config);
  },

  onShareTimeline() {
    if (share.isMockWorkerId(this.data.workerId)) {
      return share.buildHomeTimeline();
    }
    return share.buildWorkerTimeline(
      this.data.worker,
      this.data.workerId,
      this.data.shareStaffId
    );
  },

  showBookModal() {
    const agreed = wx.getStorageSync("privacyAgreed");
    if (!agreed) {
      this.setData({ showPrivacyModal: true });
      return;
    }
    this.setData({ showModal: true });
  },

  hidePrivacyModal() {
    this.setData({ showPrivacyModal: false });
  },

  goToPrivacy() {
    wx.navigateTo({ url: "/pages/privacy/index" });
  },

  goToAgreement() {
    wx.navigateTo({ url: "/pages/agreement/index" });
  },

  agreePrivacy() {
    wx.setStorageSync("privacyAgreed", true);
    this.setData({ showPrivacyModal: false, showModal: true });
  },

  preventMove() {},

  hideBookModal() {
    this.setData({ showModal: false });
  },

  onNameInput(e) {
    this.setData({ "form.name": e.detail.value });
  },

  onPhoneInput(e) {
    this.setData({ "form.phone": e.detail.value });
  },

  onDemandInput(e) {
    this.setData({ "form.demand": e.detail.value });
  },

  submitLead() {
    const name = (this.data.form.name || "").trim();
    const phone = this.data.form.phone || "";
    const demand = (this.data.form.demand || "").trim();

    if (!name) {
      wx.showToast({ title: "请填写称呼", icon: "none" });
      return;
    }
    if (!/^1\d{10}$/.test(phone)) {
      wx.showToast({ title: "手机号格式不对", icon: "none" });
      return;
    }

    wx.showLoading({ title: "提交中" });
    api.submitLead({
      worker_id: this.data.workerId,
      share_staff_id: this.data.shareStaffId || undefined,
      customer_name: name,
      customer_phone: phone,
      demand_detail: demand || undefined,
      source: "wx_mini_program"
    })
      .then(() => {
        wx.hideLoading();
        tracker.trackLeadSuccess({
          worker_id: this.data.workerId,
          page: "detail",
          source: "wx_mini_program"
        });
        wx.showToast({ title: "提交成功", icon: "success" });
        this.hideBookModal();
        this.setData({ form: { name: "", phone: "", demand: "" } });
      })
      .catch((err) => {
        wx.hideLoading();
        console.error("submit lead failed", err);
      });
  }
});
