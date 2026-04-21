<template>
  <div class="page">
    <div class="toolbar card">
      <el-input
        v-model="keyword"
        placeholder="请输入员工姓名、昵称、身份证号或手机号"
        clearable
        class="search-input"
        @keyup.enter="loadStaff"
      />
      <div class="toolbar-right">
        <el-button @click="router.push('/staff/create')">新建员工</el-button>
        <el-select v-model="status" placeholder="状态" clearable @change="loadStaff">
          <el-option label="启用" value="active" />
          <el-option label="禁用" value="disabled" />
        </el-select>
        <el-button type="primary" @click="loadStaff">查询</el-button>
      </div>
    </div>

    <div class="card table-card">
      <el-table v-loading="loading" :data="rows">
        <el-table-column prop="real_name" label="真实姓名" min-width="120">
          <template #default="{ row }">{{ row.real_name || row.nickname || "-" }}</template>
        </el-table-column>
        <el-table-column prop="nickname" label="昵称" min-width="140">
          <template #default="{ row }">{{ row.nickname || "-" }}</template>
        </el-table-column>
        <el-table-column prop="id_card" label="身份证号" min-width="220">
          <template #default="{ row }">{{ row.id_card || "-" }}</template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" min-width="140">
          <template #default="{ row }">{{ row.phone || "-" }}</template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">{{ row.role === "staff" ? "员工" : row.role || "-" }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === "active" ? "启用" : "禁用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
        <el-table-column prop="last_login_at" label="最近登录" min-width="180">
          <template #default="{ row }">{{ formatDate(row.last_login_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="320">
          <template #default="{ row }">
            <el-space>
              <el-button type="primary" link @click="router.push(`/staff/detail/${row.id}`)">查看详情</el-button>
              <el-button type="success" link @click="router.push(`/staff/edit/${row.id}`)">编辑信息</el-button>
              <el-button type="primary" link @click="toggleStatus(row)">
                {{ row.status === "active" ? "设为禁用" : "设为启用" }}
              </el-button>
              <el-button type="warning" link @click="resetPassword(row)">重置密码</el-button>
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
          @current-change="loadStaff"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onActivated, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { getUsersApi, resetUserPasswordApi, updateUserStatusApi, deleteStaffApi } from "@/api/modules/business";
import { formatDate } from "@/utils";

const router = useRouter();
const loading = ref(false);
const rows = ref<any[]>([]);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const keyword = ref("");
const status = ref("");

const loadStaff = async () => {
  loading.value = true;
  try {
    const response = (await getUsersApi({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
      role: "staff",
      status: status.value || undefined
    })) as any;
    const data = response?.data ?? response ?? {};
    rows.value = Array.isArray(data.list) ? data.list : [];
    total.value = Number(data.total || 0);
  } finally {
    loading.value = false;
  }
};

const toggleStatus = async (row: any) => {
  const nextStatus = row.status === "active" ? "disabled" : "active";
  await updateUserStatusApi(row.id, nextStatus);
  row.status = nextStatus;
  ElMessage.success(nextStatus === "active" ? "员工已启用" : "员工已禁用");
};

const resetPassword = async (row: any) => {
  const accountLabel = row.id_card || row.real_name || row.nickname || row.email || `用户#${row.id}`;
  const { value } = await ElMessageBox.prompt(`请输入 ${accountLabel} 的新密码`, "重置密码", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    inputPattern: /^.{6,}$/,
    inputErrorMessage: "密码长度至少 6 位"
  });
  await resetUserPasswordApi(row.id, value);
  ElMessage.success("密码重置成功");
};

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm("确定要删除该员工账号吗？此操作不可恢复。", "删除确认", {
      confirmButtonText: "删除",
      cancelButtonText: "取消",
      type: "warning"
    });
    await deleteStaffApi(row.id);
    ElMessage.success("删除成功");
    loadStaff();
  } catch (e) {
    if (e !== "cancel") {
      console.error(e);
    }
  }
};

onMounted(loadStaff);
onActivated(loadStaff);
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
  max-width: 360px;
}

.toolbar-right {
  display: flex;
  gap: 12px;
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
