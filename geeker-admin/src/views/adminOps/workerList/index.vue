<template>
  <div class="page">
    <div class="toolbar card">
      <div class="toolbar-left">
        <el-input
          v-model="keyword"
          placeholder="搜索姓名、手机号、身份证号"
          clearable
          class="search-input"
          @keyup.enter="loadWorkers"
        />
        <el-input
          v-model="address"
          placeholder="居住地点"
          clearable
          class="field-input"
          @keyup.enter="loadWorkers"
        />
        <el-input
          v-model="serviceArea"
          placeholder="服务区域"
          clearable
          class="field-input"
          @keyup.enter="loadWorkers"
        />
        <el-select v-model="jobType" placeholder="接单类型" clearable class="field-select" @change="loadWorkers">
          <el-option v-for="item in jobTypeOptions" :key="item" :label="item" :value="item" />
        </el-select>
        <el-select v-model="currentStatus" placeholder="当前状态" clearable class="field-select" @change="loadWorkers">
          <el-option label="可接单" value="available" />
          <el-option label="服务中" value="on_job" />
          <el-option label="暂停接单" value="paused" />
          <el-option label="黑名单" value="blacklisted" />
          <el-option label="停用" value="inactive" />
        </el-select>
        <el-select v-model="availability" placeholder="是否可接单" clearable class="field-select" @change="loadWorkers">
          <el-option label="可接单" :value="true" />
          <el-option label="不可接单" :value="false" />
        </el-select>
        <div class="age-range">
          <el-input-number v-model="minAge" :min="18" :max="70" placeholder="最小年龄" class="age-input" />
          <span class="age-sep">-</span>
          <el-input-number v-model="maxAge" :min="18" :max="70" placeholder="最大年龄" class="age-input" />
        </div>
        <el-button type="primary" @click="loadWorkers">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>

      <div class="toolbar-right">
        <el-button v-if="isAdmin" @click="router.push('/worker/create')">新建阿姨档案</el-button>
        <el-button @click="downloadTemplate">下载模板</el-button>
        <el-button @click="triggerImport">导入阿姨</el-button>
        <el-button v-if="isAdmin" type="success" :loading="exporting" @click="exportWorkers">导出阿姨</el-button>
      </div>
    </div>

    <input ref="importInputRef" type="file" accept=".xlsx,.xls" class="hidden-input" @change="handleImportChange" />

    <div class="card table-card">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="created_at" label="新建日期" min-width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="real_name" label="姓名" min-width="120" />
        <el-table-column prop="phone" label="手机号" min-width="140" />
        <el-table-column prop="id_card" label="身份证号" min-width="190" show-overflow-tooltip />
        <el-table-column prop="gender" label="性别" width="90">
          <template #default="{ row }">{{ row.gender === "female" ? "女" : row.gender === "male" ? "男" : "-" }}</template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="90" />
        <el-table-column label="接单类型" min-width="220">
          <template #default="{ row }">
            <el-space wrap>
              <el-tag v-for="item in row.job_types || []" :key="item" size="small">{{ item }}</el-tag>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="居住地点" min-width="180" show-overflow-tooltip />
        <el-table-column label="服务区域" min-width="180">
          <template #default="{ row }">{{ (row.service_areas || []).join("、") || "-" }}</template>
        </el-table-column>
        <el-table-column label="技能标签" min-width="220">
          <template #default="{ row }">
            <el-space wrap>
              <el-tag v-for="skill in row.skills || []" :key="skill" size="small" effect="plain">{{ skill }}</el-tag>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column label="当前状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.current_status] || 'info'">
              {{ statusTextMap[row.current_status] || row.current_status || "-" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="可接单" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_available ? 'success' : 'info'">{{ row.is_available ? "是" : "否" }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="320">
          <template #default="{ row }">
            <el-space>
              <el-button type="primary" link @click="router.push(`/worker/detail/${row.user_id}`)">查看详情</el-button>
              <el-button type="success" link @click="router.push(`/worker/edit/${row.user_id}`)">编辑档案</el-button>
              <el-switch
                :model-value="row.is_available"
                inline-prompt
                active-text="开"
                inactive-text="关"
                @change="toggleAvailable(row)"
              />
              <el-button type="warning" link @click="toggleRecommend(row)">
                {{ row.is_recommended ? "取消推荐" : "设为推荐" }}
              </el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
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
          @current-change="loadWorkers"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onActivated, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  downloadWorkerTemplateApi,
  exportWorkersApi,
  getWorkersApi,
  importWorkersApi,
  updateWorkerAvailableApi,
  updateWorkerRecommendApi,
  deleteWorkerApi
} from "@/api/modules/business";
import { useUserStore } from "@/stores/modules/user";
import { formatDate } from "@/utils";

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
const address = ref("");
const serviceArea = ref("");
const jobType = ref("");
const currentStatus = ref("");
const availability = ref<boolean | undefined>();
const minAge = ref<number | undefined>();
const maxAge = ref<number | undefined>();
const importInputRef = ref<HTMLInputElement>();

const jobTypeOptions = [
  "白班保姆",
  "住家保姆",
  "月嫂",
  "白班育儿嫂",
  "住家育儿嫂",
  "钟点工",
  "护工"
];

const statusTextMap: Record<string, string> = {
  available: "可接单",
  on_job: "服务中",
  paused: "暂停接单",
  blacklisted: "黑名单",
  inactive: "停用"
};

const statusTypeMap: Record<string, "info" | "warning" | "success" | "danger"> = {
  available: "success",
  on_job: "warning",
  paused: "info",
  blacklisted: "danger",
  inactive: "info"
};

const buildParams = () => ({
  page: page.value,
  page_size: pageSize.value,
  keyword: keyword.value || undefined,
  address: address.value || undefined,
  service_area: serviceArea.value || undefined,
  job_type: jobType.value || undefined,
  current_status: currentStatus.value || undefined,
  is_available: availability.value,
  min_age: minAge.value,
  max_age: maxAge.value
});

const loadWorkers = async () => {
  loading.value = true;
  try {
    const response = (await getWorkersApi(buildParams())) as any;
    const data = response?.data ?? response ?? {};
    rows.value = Array.isArray(data.list) ? data.list : [];
    total.value = Number(data.total || 0);
  } finally {
    loading.value = false;
  }
};

const resetFilters = () => {
  keyword.value = "";
  address.value = "";
  serviceArea.value = "";
  jobType.value = "";
  currentStatus.value = "";
  availability.value = undefined;
  minAge.value = undefined;
  maxAge.value = undefined;
  page.value = 1;
  loadWorkers();
};

const toggleAvailable = async (row: any) => {
  await updateWorkerAvailableApi(row.id, !row.is_available);
  row.is_available = !row.is_available;
  ElMessage.success(row.is_available ? "已开启接单" : "已暂停接单");
};

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm("确定要删除该阿姨档案吗？此操作不可恢复。", "删除确认", {
      confirmButtonText: "删除",
      cancelButtonText: "取消",
      type: "warning"
    });
    await deleteWorkerApi(row.id);
    ElMessage.success("删除成功");
    loadWorkers();
  } catch (e) {
    if (e !== "cancel") {
      console.error(e);
    }
  }
};

const toggleRecommend = async (row: any) => {
  await updateWorkerRecommendApi(row.id, !row.is_recommended);
  row.is_recommended = !row.is_recommended;
  ElMessage.success(row.is_recommended ? "已设为首页推荐" : "已取消首页推荐");
};

const exportWorkers = async () => {
  if (!isAdmin) return;
  exporting.value = true;
  try {
    const blob = (await exportWorkersApi({
      keyword: keyword.value || undefined,
      address: address.value || undefined,
      service_area: serviceArea.value || undefined,
      job_type: jobType.value || undefined,
      current_status: currentStatus.value || undefined,
      is_available: availability.value,
      min_age: minAge.value,
      max_age: maxAge.value
    })) as unknown as Blob;
    if (!(blob instanceof Blob)) {
      ElMessage.error("导出失败：返回数据不是文件流");
      return;
    }
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `阿姨名单_${new Date().toISOString().slice(0, 10)}.xlsx`;
    link.click();
    window.URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } finally {
    exporting.value = false;
  }
};

const downloadTemplate = async () => {
  const blob = (await downloadWorkerTemplateApi()) as unknown as Blob;
  if (!(blob instanceof Blob)) {
    ElMessage.error("模板下载失败：返回数据不是文件流");
    return;
  }
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "阿姨导入模板.xlsx";
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
    const response = (await importWorkersApi(formData)) as any;
    const data = response?.data ?? {};
    ElMessage.success(`导入完成：成功 ${data.success ?? 0} 条，失败 ${data.failed ?? 0} 条`);
    await loadWorkers();
  } finally {
    importing.value = false;
    input.value = "";
  }
};

onMounted(loadWorkers);
onActivated(loadWorkers);
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
  flex-direction: column;
  gap: 12px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.search-input {
  width: 240px;
}

.field-input,
.field-select {
  width: 160px;
}

.age-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.age-input {
  width: 120px;
}

.age-sep {
  color: var(--el-text-color-secondary);
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
  .toolbar-left,
  .toolbar-right,
  .age-range {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input,
  .field-input,
  .field-select,
  .age-input {
    width: 100%;
  }
}
</style>
