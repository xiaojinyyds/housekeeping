const api = require("../../utils/api.js");

const JOB_TYPE_OPTIONS = [
  "全部",
  "白班保姆",
  "住家保姆",
  "月嫂",
  "白班育儿嫂",
  "住家育儿嫂",
  "钟点工",
  "护工",
  "保姆"
];

const MOCK_WORKER = {
  id: "mock-worker-profile-1",
  user_id: "mock-worker-user-1",
  real_name: "何阿姨",
  display_name: "何**",
  age: 43,
  gender: "female",
  phone: "13800138000",
  address: "浦东新区张江镇",
  experience_years: 8,
  skills: ["做饭", "保洁", "带娃", "辅食"],
  job_types: ["白班育儿嫂", "白班保姆"],
  service_areas: ["浦东新区", "花木", "张江"],
  current_status: "available",
  status_text: "可预约",
  is_available: true,
  is_recommended: true,
  completed_orders: 126,
  rating: 4.9,
  avatar_url: "https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0"
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
    workers: [],
    page: 1,
    pageSize: 10,
    loading: false,
    noMore: false,
    selectedQuickFilter: "all",
    keywordInput: "",
    serviceAreaInput: "",
    jobTypeOptions: JOB_TYPE_OPTIONS,
    jobTypeIndex: 0,
    showPrivacyModal: false,
    filters: {
      is_available: undefined,
      is_recommended: undefined,
      keyword: "",
      job_type: "",
      service_area: ""
    }
  },

  onLoad() {
    this.enableShareMenus();
    this.fetchWorkers();
    // 检查是否需要显示隐私弹窗
    const app = getApp();
    if (app.globalData.showPrivacyModal) {
      this.setData({ showPrivacyModal: true });
    }
  },

  onPrivacyAgree() {
    wx.setStorageSync('privacyAgreed', true);
    const app = getApp();
    app.globalData.showPrivacyModal = false;
    this.setData({ showPrivacyModal: false });
  },

  onPrivacyDisagree() {
    this.setData({ showPrivacyModal: false });
    wx.showToast({
      title: '需要同意隐私政策才能使用',
      icon: 'none',
      duration: 2000
    });
  },

  enableShareMenus() {
    if (!wx.showShareMenu) return;
    wx.showShareMenu({
      withShareTicket: true,
      menus: ["shareAppMessage", "shareTimeline"]
    });
  },

  onPullDownRefresh() {
    this.reloadList().finally(() => {
      wx.stopPullDownRefresh();
    });
  },

  onReachBottom() {
    if (this.data.loading || this.data.noMore) return;
    this.setData({ page: this.data.page + 1 }, () => {
      this.fetchWorkers();
    });
  },

  getNormalizedFilters() {
    return Object.assign({}, this.data.filters);
  },

  normalizeWorkers(list) {
    return (list || []).map((item) => {
      const worker = Object.assign({}, item);
      const skills = Array.isArray(worker.skills)
        ? worker.skills
        : (typeof worker.skills === "string" ? worker.skills.split(",") : []);
      const jobTypes = Array.isArray(worker.job_types)
        ? worker.job_types
        : (typeof worker.job_types === "string" ? worker.job_types.split(",") : []);

      worker.skillsArray = skills.filter(Boolean).slice(0, 4);
      worker.jobTypesText = jobTypes.filter(Boolean).join(" / ");
      worker.display_name = worker.display_name || worker.real_name || "";
      worker.status_text = worker.status_text || "";
      worker.experience_years = worker.experience_years || 0;
      worker.completed_orders = worker.completed_orders || 0;
      worker.rating = worker.rating || "5.0";
      return worker;
    });
  },

  getMockWorkers() {
    return this.normalizeWorkers([MOCK_WORKER]);
  },

  reloadList() {
    return new Promise((resolve) => {
      this.setData(
        {
          workers: [],
          page: 1,
          noMore: false
        },
        () => {
          this.fetchWorkers().finally(resolve);
        }
      );
    });
  },

  fetchWorkers() {
    if (this.data.loading) return Promise.resolve();

    this.setData({ loading: true });
    return api
      .getWorkers(this.data.page, this.data.pageSize, this.getNormalizedFilters())
      .then((res) => {
        const list = this.normalizeWorkers(res.list || []);
        const finalList = list.length ? list : (isDevtools() && this.data.page === 1 ? this.getMockWorkers() : []);
        const workers = this.data.page === 1 ? finalList : this.data.workers.concat(finalList);
        this.setData({
          workers,
          loading: false,
          noMore: res.page >= res.total_pages || finalList.length < this.data.pageSize
        });
      })
      .catch((err) => {
        console.error("fetch workers failed", err);
        if (isDevtools() && this.data.page === 1) {
          this.setData({
            workers: this.getMockWorkers(),
            loading: false,
            noMore: true
          });
          return;
        }
        this.setData({ loading: false });
      });
  },

  onQuickFilterTap(e) {
    const type = e.currentTarget.dataset.type;
    const nextFilters = {
      is_available: undefined,
      is_recommended: undefined
    };

    if (type === "available") nextFilters.is_available = true;
    if (type === "recommended") nextFilters.is_recommended = true;

    this.setData(
      {
        selectedQuickFilter: type,
        filters: Object.assign({}, this.data.filters, nextFilters)
      },
      () => {
        this.reloadList();
      }
    );
  },

  onKeywordInput(e) {
    this.setData({ keywordInput: e.detail.value || "" });
  },

  onServiceAreaInput(e) {
    this.setData({ serviceAreaInput: e.detail.value || "" });
  },

  onJobTypeChange(e) {
    const jobTypeIndex = Number(e.detail.value || 0);
    this.setData({ jobTypeIndex });
  },

  applyFilters() {
    const jobType = this.data.jobTypeOptions[this.data.jobTypeIndex];
    this.setData(
      {
        filters: Object.assign({}, this.data.filters, {
          keyword: (this.data.keywordInput || "").trim(),
          service_area: (this.data.serviceAreaInput || "").trim(),
          job_type: jobType && jobType !== "全部" ? jobType : ""
        })
      },
      () => {
        this.reloadList();
      }
    );
  },

  clearFilters() {
    this.setData(
      {
        selectedQuickFilter: "all",
        keywordInput: "",
        serviceAreaInput: "",
        jobTypeIndex: 0,
        filters: {
          is_available: undefined,
          is_recommended: undefined,
          keyword: "",
          job_type: "",
          service_area: ""
        }
      },
      () => {
        this.reloadList();
      }
    );
  },

  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/detail/index?id=${id}`
    });
  },

  onShareAppMessage() {
    return {
      title: "千陌家政，帮你更快找到合适阿姨",
      path: "/pages/index/index?from=share_app_message"
    };
  },

  onShareTimeline() {
    return {
      title: "千陌家政，帮你更快找到合适阿姨",
      query: "from=share_timeline"
    };
  }
});
