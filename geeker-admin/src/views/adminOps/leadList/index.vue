<template>
  <div class="page">
    <div class="toolbar card">
      <el-input
        v-model="keyword"
        placeholder="请输入客户姓名、电话、线索名或地址"
        clearable
        class="search-input"
        @keyup.enter="loadLeads"
      />
      <div class="toolbar-right">
        <el-button @click="router.push('/lead/create')">新建线索</el-button>
        <el-button @click="downloadTemplate">下载模板</el-button>
        <el-button @click="triggerImport">导入线索</el-button>
        <el-button v-if="isAdmin" type="success" :loading="exporting" @click="exportLeads">导出线索</el-button>
        <el-select v-model="status" placeholder="线索状态" clearable @change="loadLeads">
          <el-option label="新线索" value="new" />
          <el-option label="跟进中" value="contacting" />
          <el-option label="面试中" value="interviewing" />
          <el-option label="已签约" value="signed" />
          <el-option label="已关闭" value="closed" />
          <el-option label="无效" value="invalid" />
        </el-select>
        <el-select v-model="serviceType" placeholder="订单类型" clearable @change="loadLeads">
          <el-option label="住家保姆" value="住家保姆" />
          <el-option label="白班保姆" value="白班保姆" />
          <el-option label="住家育儿嫂" value="住家育儿嫂" />
          <el-option label="白班育儿嫂" value="白班育儿嫂" />
          <el-option label="钟点工" value="钟点工" />
          <el-option label="月嫂" value="月嫂" />
          <el-option label="护工" value="护工" />
        </el-select>
        <el-select v-model="leadCategory" placeholder="线索类别" clearable @change="loadLeads">
          <el-option label="A类" value="A" />
          <el-option label="B类" value="B" />
        </el-select>
        <el-select v-if="isAdmin" v-model="ownerStaffId" placeholder="跟进员工" clearable @change="loadLeads">
          <el-option v-for="item in staffOptions" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          class="date-range"
          @change="loadLeads"
        />
        <el-button type="primary" @click="loadLeads">查询</el-button>
      </div>
    </div>

    <input ref="importInputRef" type="file" accept=".xlsx,.xls" class="hidden-input" @change="handleImportChange" />

    <div class="card table-card">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="customer_name" label="客户称呼" min-width="120">
          <template #default="{ row }">{{ row.customer_name || "-" }}</template>
        </el-table-column>
        <el-table-column prop="phone" label="联系方式" min-width="140" />
        <el-table-column prop="source" label="客户来源" min-width="120">
          <template #default="{ row }">{{ row.source_detail || row.source || "-" }}</template>
        </el-table-column>
        <el-table-column prop="lead_date" label="线索日期" min-width="120">
          <template #default="{ row }">{{ row.lead_date || "-" }}</template>
        </el-table-column>
        <el-table-column prop="lead_category" label="线索类别" width="100">
          <template #default="{ row }">{{ row.lead_category ? `${row.lead_category}类` : "-" }}</template>
        </el-table-column>
        <el-table-column prop="service_type" label="订单类型" min-width="120" />
        <el-table-column prop="demand_address" label="需求地址" min-width="180">
          <template #default="{ row }">{{ row.demand_address || "-" }}</template>
        </el-table-column>
        <el-table-column prop="owner_staff_name" label="跟进人" width="120">
          <template #default="{ row }">{{ row.owner_staff_name || "-" }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status] || 'info'">{{ statusTextMap[row.status] || row.status || "-" }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="latest_follow_up_at" label="最近跟进" min-width="180">
          <template #default="{ row }">{{ formatDate(row.latest_follow_up_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="260">
          <template #default="{ row }">
            <el-space>
              <el-button type="primary" link @click="router.push(`/lead/detail/${row.id}`)">查看详情</el-button>
              <el-button type="success" link @click="router.push(`/lead/edit/${row.id}`)">编辑线索</el-button>
              <el-button type="success" link @click="router.push(`/lead/detail/${row.id}`)">跟进记录</el-button>
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
          @current-change="loadLeads"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onActivated, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { downloadLeadTemplateApi, exportLeadsApi, getLeadListApi, getUsersApi, importLeadsApi } from "@/api/modules/business";
import { useUserStore } from "@/stores/modules/user";
import { formatDate } from "@/utils";

const router = useRouter();
const userStore = useUserStore();
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
const leadCategory = ref<"A" | "B" | "">("");
const ownerStaffId = ref("");
const dateRange = ref<string[]>([]);
const staffOptions = ref<{ id: string; name: string }[]>([]);
const importInputRef = ref<HTMLInputElement>();
const isAdmin = userStore.userInfo?.role === "admin";

const statusTextMap: Record<string, string> = {
  new: "新线索",
  contacting: "跟进中",
  interviewing: "面试中",
  signed: "已签约",
  closed: "已关闭",
  invalid: "无效"
};

const statusTypeMap: Record<string, "info" | "warning" | "success" | "danger"> = {
  new: "info",
  contacting: "warning",
  interviewing: "warning",
  signed: "success",
  closed: "info",
  invalid: "danger"
};

const loadStaffOptions = async () => {
  if (!isAdmin) return;
  const response = (await getUsersApi({
    role: "staff",
    status: "active",
    page: 1,
    page_size: 100
  })) as any;
  const data = response?.data ?? {};
  const list = Array.isArray(data.list) ? data.list : [];
  staffOptions.value = list.map((item: any) => ({
    id: item.id,
    name: item.real_name || item.nickname || item.email || item.id
  }));
};

const exportLeads = async () => {
  if (!isAdmin) return;
  exporting.value = true;
  try {
    const blob = (await exportLeadsApi({
      status: status.value || undefined,
      service_type: serviceType.value || undefined,
      lead_category: (leadCategory.value as "A" | "B") || undefined,
      owner_staff_id: ownerStaffId.value || undefined,
      start_date: dateRange.value?.[0] || undefined,
      end_date: dateRange.value?.[1] || undefined
    })) as unknown as Blob;
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `客户线索_${new Date().toISOString().slice(0, 10)}.xlsx`;
    link.click();
    window.URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } finally {
    exporting.value = false;
  }
};

const downloadTemplate = async () => {
  const blob = (await downloadLeadTemplateApi()) as unknown as Blob;
  if (!(blob instanceof Blob)) {
    ElMessage.error("模板下载失败：返回数据不是文件流");
    return;
  }
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "线索导入模板.xlsx";
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
    const response = (await importLeadsApi(formData)) as any;
    const data = response?.data ?? {};
    ElMessage.success(`导入完成：成功 ${data.success ?? 0} 条，失败 ${data.failed ?? 0} 条`);
    await loadLeads();
  } finally {
    importing.value = false;
    input.value = "";
  }
};

const loadLeads = async () => {
  loading.value = true;
  try {
    const response = (await getLeadListApi({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
      status: status.value || undefined,
      service_type: serviceType.value || undefined,
      lead_category: (leadCategory.value as "A" | "B") || undefined,
      owner_staff_id: ownerStaffId.value || undefined,
      start_date: dateRange.value?.[0] || undefined,
      end_date: dateRange.value?.[1] || undefined
    })) as any;
    const data = response?.data ?? response ?? {};
    rows.value = Array.isArray(data.list) ? data.list : [];
    total.value = Number(data.total || 0);
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await loadStaffOptions();
  await loadLeads();
});
onActivated(loadLeads);
</script>

<style scoped lang="scss">
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar,
.table-card {
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

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 900px) {
  .toolbar,
  .toolbar-right {
    flex-direction: column;
  }
}
</style>
