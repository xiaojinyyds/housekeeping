<template>
  <div class="page">
    <div class="toolbar card">
      <div class="toolbar-left">
        <el-input v-model="customerName" placeholder="客户称呼" clearable class="search-input" @keyup.enter="loadLeads" />
        <el-input v-model="customerPhone" placeholder="手机号" clearable class="search-input" @keyup.enter="loadLeads" />
      </div>
      <div class="toolbar-right">
        <el-select v-model="status" placeholder="跟进状态" clearable @change="loadLeads">
          <el-option label="待跟进" value="pending" />
          <el-option label="已联络" value="contacted" />
          <el-option label="已转化" value="converted" />
          <el-option label="无效" value="invalid" />
        </el-select>
        <el-button type="primary" @click="loadLeads">查询</el-button>
      </div>
    </div>

    <div class="card table-card">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="customer_name" label="客户称呼" min-width="120" />
        <el-table-column prop="customer_phone" label="联系方式" min-width="140" />
        <el-table-column prop="worker_name" label="意向阿姨" min-width="120">
          <template #default="{ row }">{{ row.worker_name || "-" }}</template>
        </el-table-column>
        <el-table-column prop="source" label="客户来源" min-width="120">
          <template #default="{ row }">{{ row.source === "wx_mini_program" ? "微信小程序" : row.source }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status] || 'info'">{{ statusTextMap[row.status] || row.status || "-" }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="handling_remark" label="跟进备注" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ row.handling_remark || "-" }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="留言时间" min-width="170">
          <template #default="{ row }">{{ row.created_at?.replace("T", " ")?.slice(0, 16) || "-" }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="120">
          <template #default="{ row }">
            <el-button type="primary" link @click="openStatusModal(row)">更新状态</el-button>
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

    <!-- 状态更新弹窗 -->
    <el-dialog v-model="dialogVisible" title="更新留言状态" width="450px" destroy-on-close>
      <el-form :model="formData" label-width="80px">
        <el-form-item label="当前客户">
          <el-tag type="info">{{ currentRow?.customer_name }} ({{ currentRow?.customer_phone }})</el-tag>
        </el-form-item>
        <el-form-item label="跟进状态" required>
          <el-select v-model="formData.status" class="w-full">
            <el-option label="待跟进" value="pending" />
            <el-option label="已联络" value="contacted" />
            <el-option label="已转化" value="converted" />
            <el-option label="无效" value="invalid" />
          </el-select>
        </el-form-item>
        <el-form-item label="跟进备注">
          <el-input v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入跟进情况..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="submitStatus">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onActivated, onMounted, ref, reactive } from "vue";
import { getGuestLeadsApi, updateGuestLeadStatusApi } from "@/api/modules/business";
import { ElMessage } from "element-plus";

const loading = ref(false);
const rows = ref<any[]>([]);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const customerName = ref("");
const customerPhone = ref("");
const status = ref("");

const dialogVisible = ref(false);
const submitLoading = ref(false);
const currentRow = ref<any>(null);
const formData = reactive({
  status: "",
  remark: ""
});

const statusTextMap: Record<string, string> = {
  pending: "待跟进",
  contacted: "已联络",
  converted: "已转化",
  invalid: "无效"
};

const statusTypeMap: Record<string, "info" | "warning" | "success" | "danger" | "primary"> = {
  pending: "danger",
  contacted: "warning",
  converted: "success",
  invalid: "info"
};

const loadLeads = async () => {
  loading.value = true;
  try {
    const response = (await getGuestLeadsApi({
      page: page.value,
      page_size: pageSize.value,
      customer_name: customerName.value || undefined,
      customer_phone: customerPhone.value || undefined,
      status: status.value || undefined
    })) as any;
    const data = response?.data ?? response ?? {};
    rows.value = Array.isArray(data.list) ? data.list : [];
    total.value = Number(data.total || 0);
  } finally {
    loading.value = false;
  }
};

const openStatusModal = (row: any) => {
  currentRow.value = row;
  formData.status = row.status || "pending";
  formData.remark = row.handling_remark || "";
  dialogVisible.value = true;
};

const submitStatus = async () => {
  if (!formData.status) return ElMessage.warning("请选择状态");
  submitLoading.value = true;
  try {
    await updateGuestLeadStatusApi(currentRow.value.id, formData.status, formData.remark);
    ElMessage.success("状态更新成功");
    dialogVisible.value = false;
    loadLeads();
  } catch (error) {
    console.error(error);
  } finally {
    submitLoading.value = false;
  }
};

onMounted(loadLeads);
onActivated(loadLeads);
</script>

<style scoped lang="scss">
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
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

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
}

.search-input {
  width: 200px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.w-full {
  width: 100%;
}

@media (max-width: 900px) {
  .toolbar {
    flex-direction: column;
  }
}
</style>
