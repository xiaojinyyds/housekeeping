<template>
  <div class="workbench staff-workbench">
    <div class="hero card">
      <div>
        <p class="eyebrow">个人业绩</p>
        <h1>我的业务工作台</h1>
        <p class="summary">聚焦你本月的签单金额、客户线索跟进和阿姨档案录入情况，帮助你更直观看到自己的业务完成进度。</p>
      </div>
      <div class="hero-side">
        <div class="hero-kpi">
          <span>我本月签单金额</span>
          <strong>{{ formatMoney(dashboard.month_contract_amount) }}</strong>
        </div>
        <div class="hero-kpi">
          <span>我本月签单数</span>
          <strong>{{ dashboard.month_contract_count }}</strong>
        </div>
      </div>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="kpi card tone-blue">
          <span>我本月签单金额</span>
          <strong>{{ formatMoney(dashboard.month_contract_amount) }}</strong>
          <small>统计月份：{{ dashboard.month || "-" }}</small>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="kpi card tone-green">
          <span>我本月签单数</span>
          <strong>{{ dashboard.month_contract_count }}</strong>
          <small>我名下已签合同总量</small>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="kpi card tone-orange">
          <span>我本月线索数</span>
          <strong>{{ dashboard.month_lead_count }}</strong>
          <small>归属到我名下的客户资源</small>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="kpi card tone-red">
          <span>我本月新增阿姨</span>
          <strong>{{ dashboard.month_worker_add_count }}</strong>
          <small>我录入的新阿姨档案</small>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="14">
        <div class="card panel chart-panel">
          <div class="panel-header">
            <h3>近 7 天签单走势</h3>
            <span>我每天的签单金额和签单单数</span>
          </div>
          <div class="chart-wrap">
            <ECharts :option="contractTrendOption" />
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="10">
        <div class="card panel chart-panel">
          <div class="panel-header">
            <h3>近 7 天资源新增</h3>
            <span>我名下线索和阿姨录入新增趋势</span>
          </div>
          <div class="chart-wrap">
            <ECharts :option="growthTrendOption" />
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from "vue";
import ECharts from "@/components/ECharts/index.vue";
import type { ECOption } from "@/components/ECharts/config";
import { getStatisticsApi } from "@/api/modules/business";

const stats = reactive<any>({
  dashboard: {
    month: "",
    month_contract_amount: 0,
    month_contract_count: 0,
    month_lead_count: 0,
    month_worker_add_count: 0,
    daily_metrics: []
  }
});

const dashboard = computed(() => stats.dashboard ?? {});

const loadStatistics = async () => {
  const response = (await getStatisticsApi()) as any;
  const data = response?.data ?? {};
  Object.assign(stats, data);
};

const formatMoney = (value?: number | string | null) => {
  if (value === null || value === undefined || value === "") return "0.00";
  return Number(value).toFixed(2);
};

const contractTrendOption = computed<ECOption>(() => ({
  tooltip: { trigger: "axis" },
  legend: { top: 0 },
  grid: { left: "4%", right: "4%", bottom: "8%", top: "14%", containLabel: true },
  xAxis: {
    type: "category",
    data: (dashboard.value.daily_metrics || []).map((item: any) => item.label)
  },
  yAxis: [
    { type: "value", name: "金额" },
    { type: "value", name: "合同数" }
  ],
  series: [
    {
      name: "签单金额",
      type: "line",
      smooth: true,
      itemStyle: { color: "#2f8af5" },
      areaStyle: { color: "rgba(47, 138, 245, 0.16)" },
      data: (dashboard.value.daily_metrics || []).map((item: any) => item.contract_amount)
    },
    {
      name: "合同数",
      type: "bar",
      yAxisIndex: 1,
      barMaxWidth: 28,
      itemStyle: { color: "#24b36b", borderRadius: [6, 6, 0, 0] },
      data: (dashboard.value.daily_metrics || []).map((item: any) => item.contract_count)
    }
  ]
}));

const growthTrendOption = computed<ECOption>(() => ({
  tooltip: { trigger: "axis" },
  legend: { top: 0 },
  grid: { left: "4%", right: "4%", bottom: "8%", top: "14%", containLabel: true },
  xAxis: {
    type: "category",
    data: (dashboard.value.daily_metrics || []).map((item: any) => item.label)
  },
  yAxis: { type: "value" },
  series: [
    {
      name: "线索新增",
      type: "line",
      smooth: true,
      itemStyle: { color: "#ff9f43" },
      data: (dashboard.value.daily_metrics || []).map((item: any) => item.lead_count)
    },
    {
      name: "阿姨新增",
      type: "line",
      smooth: true,
      itemStyle: { color: "#fa5a5a" },
      data: (dashboard.value.daily_metrics || []).map((item: any) => item.worker_add_count)
    }
  ]
}));

onMounted(loadStatistics);
</script>

<style scoped lang="scss">
.workbench {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hero {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  padding: 28px;
  background:
    radial-gradient(circle at top left, rgba(47, 138, 245, 0.2), transparent 36%),
    linear-gradient(120deg, #f7faff 0%, #eef4ff 100%);
}

.eyebrow {
  margin: 0 0 10px;
  color: #2f8af5;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: 32px;
}

.summary {
  max-width: 640px;
  margin: 12px 0 0;
  color: var(--el-text-color-secondary);
  line-height: 1.8;
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hero-kpi {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 116px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.88);
}

.hero-kpi span,
.kpi span {
  color: var(--el-text-color-secondary);
}

.hero-kpi strong,
.kpi strong {
  margin-top: 10px;
  font-size: 30px;
  line-height: 1;
}

.kpi {
  display: flex;
  flex-direction: column;
  min-height: 140px;
  padding: 22px;
  border-top: 4px solid transparent;
}

.kpi small {
  margin-top: auto;
  color: var(--el-text-color-secondary);
}

.tone-blue {
  border-color: #2f8af5;
}

.tone-green {
  border-color: #24b36b;
}

.tone-orange {
  border-color: #ff9f43;
}

.tone-red {
  border-color: #fa5a5a;
}

.panel {
  height: 100%;
  padding: 22px;
}

.chart-panel {
  min-height: 392px;
}

.panel-header {
  display: flex;
  align-items: end;
  justify-content: space-between;
  margin-bottom: 18px;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
}

.panel-header span {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.chart-wrap {
  height: 320px;
}

@media (max-width: 991px) {
  .hero {
    grid-template-columns: 1fr;
  }
}
</style>
