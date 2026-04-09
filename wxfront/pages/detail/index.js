const api = require("../../utils/api.js");
const tracker = require("../../utils/tracker.js");

const MOCK_WORKER_ID = "mock-worker-user-1";
const MOCK_WORKER_DETAIL = {
  id: "mock-worker-profile-1",
  user_id: MOCK_WORKER_ID,
  real_name: "何阿姨",
  display_name: "何**",
  age: 43,
  gender: "female",
  phone: "13800138000",
  id_card: "310101198301011234",
  address: "浦东新区张江镇",
  experience_years: 8,
  skills: ["做饭", "保洁", "带娃", "辅食添加"],
  job_types: ["白班育儿嫂", "白班保姆"],
  service_areas: ["浦东新区", "花木", "张江"],
  current_status: "available",
  status_text: "可预约",
  introduction: "有多年母婴护理和家庭照护经验，做事细致，沟通温和，擅长带小月龄宝宝，也能兼顾家务整理与一日三餐。",
  recommended_reasons: [
    "性格温和，沟通耐心",
    "带小月龄宝宝经验丰富",
    "会做宝宝辅食和家常菜"
  ],
  work_experiences: [
    {
      id: "mock-exp-1",
      start_date: "2021-03-01",
      end_date: "2023-08-31",
      company_name: "浦东三口之家",
      job_content: "负责1岁宝宝日常照护、辅食制作、玩教陪伴，并兼顾家庭卫生整理。"
    },
    {
      id: "mock-exp-2",
      start_date: "2018-06-01",
      end_date: "2021-02-28",
      company_name: "花木住家家庭",
      job_content: "负责老人陪护、做饭保洁、日常陪诊和家庭生活照料。"
    }
  ],
  other_certificates: [],
  id_card_front: "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
  id_card_back: "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
  health_certificate: "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
  health_report: "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
  practice_certificate: "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
  avatar_url: "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
  rating: 4.9,
  total_orders: 148,
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
    worker: null,
    loading: true,
    showModal: false,
    defaultAvatar: "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0",
    form: { name: "", phone: "" }
  },

  onLoad(options) {
    this.enableShareMenus();
    const id = options && options.id;
    if (!id) {
      wx.showToast({ title: "参数错误", icon: "none" });
      setTimeout(() => wx.navigateBack(), 1200);
      return;
    }
    this.setData({ workerId: id });
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

    worker.display_name = worker.display_name || worker.real_name || "";
    worker.skillsArray = skills.filter(Boolean);
    worker.jobTypesText = Array.isArray(worker.job_types) ? worker.job_types.join(" / ") : "";
    worker.serviceAreasText = Array.isArray(worker.service_areas) ? worker.service_areas.join(" / ") : "";
    worker.phone_masked = this.maskPhone(worker.phone);
    worker.id_card_masked = this.maskIdCard(worker.id_card);
    worker.statusText = worker.status_text || "待确认";
    worker.certImages = this.collectCertImages(worker);
    worker.recommendedReasons = Array.isArray(worker.recommended_reasons) ? worker.recommended_reasons : [];
    worker.workExperiences = Array.isArray(worker.work_experiences) ? worker.work_experiences : [];
    worker.experience_years = worker.experience_years || 0;
    worker.rating = worker.rating || 5.0;
    worker.total_orders = worker.total_orders || 0;
    worker.completed_orders = worker.completed_orders || 0;
    return worker;
  },

  collectCertImages(worker) {
    const certImages = [];
    const add = (url, label) => {
      if (url) certImages.push({ url, label });
    };
    add(worker.id_card_front, "身份证正面");
    add(worker.id_card_back, "身份证反面");
    add(worker.health_certificate, "健康证");
    add(worker.health_report, "体检报告");
    add(worker.practice_certificate, "职业证书");
    if (Array.isArray(worker.other_certificates)) {
      worker.other_certificates.forEach((url, idx) => add(url, `其他证件${idx + 1}`));
    }
    return certImages;
  },

  maskPhone(phone) {
    if (!phone || phone.length < 7) return "";
    return `${phone.substring(0, 3)}****${phone.substring(7)}`;
  },

  maskIdCard(idCard) {
    if (!idCard || idCard.length < 14) return "";
    return `${idCard.substring(0, 6)}********${idCard.substring(14)}`;
  },

  previewCert(e) {
    const url = e.currentTarget.dataset.url;
    const worker = this.data.worker || {};
    const urls = (worker.certImages || []).map((item) => item.url);
    wx.previewImage({ current: url, urls });
  },

  onShareAppMessage() {
    const worker = this.data.worker;
    const workerId = this.data.workerId;
    return {
      title: worker ? `${worker.display_name}的阿姨档案` : "阿姨档案详情",
      path: `/pages/detail/index?id=${workerId}&from=share_app_message`,
      imageUrl: worker && worker.avatar_url ? worker.avatar_url : undefined
    };
  },

  onShareTimeline() {
    const worker = this.data.worker;
    const workerId = this.data.workerId;
    return {
      title: worker ? `${worker.display_name}的阿姨档案` : "阿姨档案详情",
      query: `id=${workerId}&from=share_timeline`
    };
  },

  showBookModal() {
    this.setData({ showModal: true });
  },

  hideBookModal() {
    this.setData({ showModal: false });
  },

  onNameInput(e) {
    this.setData({ "form.name": e.detail.value });
  },

  onPhoneInput(e) {
    this.setData({ "form.phone": e.detail.value });
  },

  submitLead() {
    const name = (this.data.form.name || "").trim();
    const phone = this.data.form.phone || "";

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
      customer_name: name,
      customer_phone: phone,
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
        this.setData({ "form.name": "", "form.phone": "" });
      })
      .catch((err) => {
        wx.hideLoading();
        console.error("submit lead failed", err);
      });
  }
});
