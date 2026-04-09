<template>
  <div class="page">
    <div class="toolbar card">
      <el-input
        v-model="keyword"
        placeholder="请输入合同编号、客户姓名、电话或服务地址"
        clearable
        class="search-input"
        @keyup.enter="loadContracts"
      />
      <div class="toolbar-right">
        <el-button @click="router.push('/contract/create')">新建合同</el-button>
        <el-button @click="downloadTemplate">下载模板</el-button>
        <el-button @click="triggerImport">导入合同</el-button>
        <el-button v-if="isAdmin" type="success" :loading="exporting" @click="exportContracts">导出合同</el-button>
        <el-select v-model="status" placeholder="合同状态" clearable @change="loadContracts">
          <el-option label="待上户" value="pending_start" />
          <el-option label="服务中" value="serving" />
          <el-option label="已暂停" value="paused" />
          <el-option label="已完成" value="completed" />
          <el-option label="已终止" value="terminated" />
          <el-option label="已退款" value="refunded" />
        </el-select>
        <el-select v-model="serviceType" placeholder="订单类型" clearable @change="loadContracts">
          <el-option label="住家保姆" value="住家保姆" />
          <el-option label="白班保姆" value="白班保姆" />
          <el-option label="住家育儿嫂" value="住家育儿嫂" />
          <el-option label="白班育儿嫂" value="白班育儿嫂" />
          <el-option label="钟点工" value="钟点工" />
          <el-option label="月嫂" value="月嫂" />
          <el-option label="护工" value="护工" />
        </el-select>
        <el-select v-if="isAdmin" v-model="brokerStaffId" placeholder="签单员工" clearable @change="loadContracts">
          <el-option v-for="item in staffOptions" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          class="date-range"
          @change="loadContracts"
        />
        <el-button type="primary" @click="loadContracts">查询</el-button>
      </div>
    </div>

    <input ref="importInputRef" type="file" accept=".xlsx,.xls" class="hidden-input" @change="handleImportChange" />

    <div class="card stats-card">
      <div class="stat-item">
        <div class="label">签单总数</div>
        <div class="value">{{ stats.contract_count }}</div>
      </div>
      <div class="stat-item">
        <div class="label">签单总金额</div>
        <div class="value">￥{{ formatMoney(stats.total_contract_amount) }}</div>
      </div>
    </div>

    <div v-if="isAdmin" class="card rank-card">
      <div class="rank-header">
        <div class="title">员工签单排行</div>
        <div class="sub">按当前筛选条件统计</div>
      </div>
      <div v-if="staffRankList.length" class="rank-list">
        <div v-for="item in staffRankList" :key="item.staff_id" class="rank-item">
          <div class="left">
            <span class="badge">#{{ item.rank }}</span>
            <span class="name">{{ item.staff_name || item.staff_id }}</span>
          </div>
          <div class="right">
            <span>{{ item.contract_count }} 单</span>
            <span>￥{{ formatMoney(item.total_contract_amount) }}</span>
          </div>
        </div>
      </div>
      <div v-else class="empty-rank">暂无排行数据</div>
    </div>

    <div class="card table-card">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="contract_no" label="合同编号" min-width="160" />
        <el-table-column prop="contract_date" label="合同日期" min-width="120">
          <template #default="{ row }">{{ row.contract_date || "-" }}</template>
        </el-table-column>
        <el-table-column prop="customer_name" label="客户姓名" min-width="120" />
        <el-table-column prop="customer_phone" label="客户电话" min-width="140" />
        <el-table-column prop="worker_name" label="阿姨姓名" min-width="120" />
        <el-table-column prop="service_type" label="订单类型" min-width="120" />
        <el-table-column prop="service_address" label="服务地址" min-width="220" show-overflow-tooltip />
        <el-table-column prop="contract_amount" label="签单金额" min-width="120">
          <template #default="{ row }">{{ formatMoney(row.contract_amount) }}</template>
        </el-table-column>
        <el-table-column prop="actual_received" label="实收金额" min-width="120">
          <template #default="{ row }">{{ formatMoney(row.actual_received) }}</template>
        </el-table-column>
        <el-table-column prop="broker_staff_name" label="签单员工" min-width="120" />
        <el-table-column prop="status" label="合同状态" min-width="120">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status] || 'info'">{{ statusTextMap[row.status] || row.status || "-" }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="latest_follow_up_at" label="最近回访" min-width="180">
          <template #default="{ row }">{{ row.latest_follow_up_at || "-" }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <el-space>
              <el-button type="primary" link @click="router.push(`/contract/detail/${row.id}`)">查看详情</el-button>
              <el-button type="success" link @click="router.push(`/contract/detail/${row.id}`)">回访记录</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          layout="total, prev, pager, next"
          :total="total"
          @current-change="loadContracts"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onActivated, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import {
  downloadContractTemplateApi,
  exportContractsApi,
  getContractStaffSummaryApi,
  getContractListApi,
  getUsersApi,
  importContractsApi
} from "@/api/modules/business";
import { useUserStore } from "@/stores/modules/user";

const router = useRouter();
const userStore = useUserStore();
const isAdmin = userStore.userInfo?.role === "admin";

const loading = ref(false);
const exporting = ref(false);
const importing = ref(false);
const rows = ref<any[]>([]);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const keyword = ref("");
const status = ref("");
const serviceType = ref("");
const brokerStaffId = ref("");
const dateRange = ref<string[]>([]);
const staffOptions = ref<{ id: string; name: string }[]>([]);
const importInputRef = ref<HTMLInputElement>();
const stats = ref({ contract_count: 0, total_contract_amount: 0 });
const staffRankList = ref<any[]>([]);

const statusTextMap: Record<string, string> = {
  pending_start: "待上户",
  serving: "服务中",
  paused: "已暂停",
  completed: "已完成",
  terminated: "已终止",
  refunded: "已退款"
};

const statusTypeMap: Record<string, "info" | "warning" | "success" | "danger"> = {
  pending_start: "warning",
  serving: "success",
  paused: "info",
  completed: "success",
  terminated: "danger",
  refunded: "danger"
};

const formatMoney = (value?: number | null) => {
  if (value === null || value === undefined || value === "") return "0.00";
  return Number(value).toFixed(2);
};

const loadStaffOptions = async () => {
  if (!isAdmin) return;
  const response = (await getUsersApi({
    role: "staff",
    status: "active",
    page: 1,
    page_size: 100
  })) as any;
  const list = Array.isArray(response?.data?.list) ? response.data.list : [];
  staffOptions.value = list.map((item: any) => ({
    id: item.id,
    name: item.real_name || item.nickname || item.email || item.id
  }));
};

const exportContracts = async () => {
  if (!isAdmin) return;
  exporting.value = true;
  try {
    const blob = (await exportContractsApi({
      broker_staff_id: brokerStaffId.value || undefined,
      status: status.value || undefined,
      service_type: serviceType.value || undefined,
      start_date: dateRange.value?.[0] || undefined,
      end_date: dateRange.value?.[1] || undefined
    })) as unknown as Blob;
    if (!(blob instanceof Blob)) {
      ElMessage.error("导出失败：返回数据不是文件流");
      return;
    }
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `合同数据_${new Date().toISOString().slice(0, 10)}.xlsx`;
    link.click();
    window.URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } finally {
    exporting.value = false;
  }
};

const downloadTemplate = async () => {
  const blob = (await downloadContractTemplateApi()) as unknown as Blob;
  if (!(blob instanceof Blob)) {
    ElMessage.error("模板下载失败：返回数据不是文件流");
    return;
  }
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "合同导入模板.xlsx";
  link.click();
  window.URL.revokeObjectURL(url);
};

const triggerImport = () => {
  if (importing.value) return;
  importInputRef.value?.click();
};

const handleImportChange = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;

  importing.value = true;
  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = (await importContractsApi(formData)) as any;
    const data = response?.data ?? {};
    ElMessage.success(`导入完成：成功 ${data.success ?? 0} 条，失败 ${data.failed ?? 0} 条`);
    await loadContracts();
  } finally {
    importing.value = false;
    input.value = "";
  }
};

const loadContracts = async () => {
  loading.value = true;
  try {
    const [listResponse, summaryResponse] = await Promise.all([
      getContractListApi({
        page: page.value,
        page_size: pageSize.value,
        keyword: keyword.value || undefined,
        status: status.value || undefined,
        service_type: serviceType.value || undefined,
        broker_staff_id: isAdmin ? brokerStaffId.value || undefined : undefined,
        start_date: dateRange.value?.[0] || undefined,
        end_date: dateRange.value?.[1] || undefined
      }),
      isAdmin
        ? getContractStaffSummaryApi({
            status: status.value || undefined,
            service_type: serviceType.value || undefined,
            broker_staff_id: brokerStaffId.value || undefined,
            start_date: dateRange.value?.[0] || undefined,
            end_date: dateRange.value?.[1] || undefined
          })
        : Promise.resolve({ data: { list: [] } } as any)
    ]);

    const data = (listResponse as any)?.data ?? listResponse ?? {};
    rows.value = Array.isArray(data.list) ? data.list : [];
    total.value = Number(data.total || 0);
    stats.value = {
      contract_count: Number(data?.stats?.contract_count || 0),
      total_contract_amount: Number(data?.stats?.total_contract_amount || 0)
    };

    if (isAdmin) {
      const summaryData = (summaryResponse as any)?.data ?? {};
      staffRankList.value = Array.isArray(summaryData.list) ? summaryData.list.slice(0, 8) : [];
    }
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await loadStaffOptions();
  await loadContracts();
});
onActivated(loadContracts);
</script>

<style scoped lang="scss">
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar,
.table-card,
.stats-card {
  padding: 16px 18px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.search-input {
  width: 320px;
  flex: 0 0 auto;
}

.toolbar-right {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.toolbar-right :deep(.el-select) {
  width: 140px;
}

.date-range {
  width: 260px;
}

.hidden-input {
  display: none;
}

.stats-card {
  display: flex;
  gap: 24px;
}

.rank-card {
  padding: 16px 18px;
}

.rank-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 10px;
}

.rank-header .title {
  font-weight: 700;
}

.rank-header .sub {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rank-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f7f9fb;
  border-radius: 10px;
  padding: 10px 12px;
}

.rank-item .left,
.rank-item .right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rank-item .badge {
  color: var(--el-color-primary);
  font-weight: 700;
}

.rank-item .name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-rank {
  color: var(--el-text-color-secondary);
}

.stat-item .label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.stat-item .value {
  margin-top: 4px;
  font-size: 24px;
  font-weight: 700;
  color: var(--el-color-primary);
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 900px) {
  .toolbar,
  .toolbar-right,
  .stats-card {
    flex-direction: column;
  }
}
</style>
