<template>
  <div class="workbench">
    <div class="hero card">
      <div>
        <p class="eyebrow">经营总览</p>
        <h1>家政业务总工作台</h1>
        <p class="summary">聚焦本月签单业绩、客户线索储备和阿姨档案新增情况，帮助你快速掌握团队整体经营节奏。</p>
      </div>
      <div class="hero-side">
        <div class="hero-kpi">
          <span>本月总签单金额</span>
          <strong>{{ formatMoney(dashboard.month_contract_amount) }}</strong>
        </div>
        <div class="hero-kpi">
          <span>本月总签单数</span>
          <strong>{{ dashboard.month_contract_count }}</strong>
        </div>
      </div>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="kpi card tone-blue">
          <span>本月总签单金额</span>
          <strong>{{ formatMoney(dashboard.month_contract_amount) }}</strong>
          <small>统计月份：{{ dashboard.month || "-" }}</small>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="kpi card tone-green">
          <span>本月总签单数</span>
          <strong>{{ dashboard.month_contract_count }}</strong>
          <small>全公司已签合同总量</small>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="kpi card tone-orange">
          <span>本月新增客户线索</span>
          <strong>{{ dashboard.month_lead_count }}</strong>
          <small>进入后台的客户资源总量</small>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="kpi card tone-red">
          <span>本月新增阿姨档案</span>
          <strong>{{ dashboard.month_worker_add_count }}</strong>
          <small>已录入档案库的新增阿姨</small>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="14">
        <div class="card panel chart-panel">
          <div class="panel-header">
            <h3>近 7 天签单走势</h3>
            <span>每天的签单金额和签单单数</span>
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
            <span>客户线索与阿姨档案新增趋势</span>
          </div>
          <div class="chart-wrap">
            <ECharts :option="growthTrendOption" />
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="14">
        <div class="card panel chart-panel">
          <div class="panel-header">
            <h3>员工签单业绩排行</h3>
            <span>按本月签单金额从高到低排序</span>
          </div>
          <div class="chart-wrap">
            <ECharts :option="staffRankingOption" />
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="10">
        <div class="card panel">
          <div class="panel-header">
            <h3>员工业绩明细</h3>
            <span>本月员工签单与资源数据</span>
          </div>
          <div class="rank-list" v-if="dashboard.staff_ranking.length">
            <div v-for="item in dashboard.staff_ranking.slice(0, 8)" :key="item.staff_id" class="rank-item">
              <div class="left">
                <span class="badge">#{{ item.rank }}</span>
                <span class="name">{{ item.staff_name }}</span>
              </div>
              <div class="right">
                <span>{{ item.contract_count }} 单</span>
                <span>{{ formatMoney(item.contract_amount) }}</span>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无排行数据" />
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
  users: { total: 0, month: 0, role_distribution: { user: 0, staff: 0, worker: 0, admin: 0 } },
  workers: { total: 0, today: 0, available: 0, avg_rating: 0 },
  applications: { pending: 0, today: 0 },
  dashboard: {
    month: "",
    month_contract_amount: 0,
    month_contract_count: 0,
    month_lead_count: 0,
    month_worker_add_count: 0,
    daily_metrics: [],
    staff_ranking: []
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
      itemStyle: { color: "#19be6b", borderRadius: [6, 6, 0, 0] },
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

const staffRankingOption = computed<ECOption>(() => {
  const list = (dashboard.value.staff_ranking || []).slice(0, 8);
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: "4%", right: "4%", bottom: "8%", top: "8%", containLabel: true },
    xAxis: { type: "value" },
    yAxis: {
      type: "category",
      inverse: true,
      data: list.map((item: any) => item.staff_name)
    },
    series: [
      {
        type: "bar",
        barMaxWidth: 20,
        itemStyle: { color: "#7d58d4", borderRadius: [0, 8, 8, 0] },
        data: list.map((item: any) => item.contract_amount)
      }
    ]
  };
});

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
    radial-gradient(circle at top left, rgba(0, 150, 136, 0.18), transparent 36%),
    linear-gradient(135deg, #f7fbfa 0%, #eef7f4 100%);
}

.eyebrow {
  margin: 0 0 10px;
  color: #009688;
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
  background: rgba(255, 255, 255, 0.8);
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
  border-color: #3f8cff;
}

.tone-green {
  border-color: #19be6b;
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

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rank-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-radius: 14px;
  background: #f7f9fb;
}

.left,
.right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.badge {
  color: var(--el-color-primary);
  font-weight: 700;
}

.name {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 991px) {
  .hero {
    grid-template-columns: 1fr;
  }
}
</style>
