<template>
  <div class="page">
    <div class="toolbar card">
      <el-input v-model="keyword" placeholder="请输入邮箱、手机号或昵称" clearable class="search-input" @keyup.enter="loadUsers" />
      <div class="toolbar-right">
        <el-select v-model="role" placeholder="角色" clearable @change="loadUsers">
          <el-option label="普通用户" value="user" />
          <el-option label="员工" value="staff" />
          <el-option label="阿姨" value="worker" />
          <el-option label="管理员" value="admin" />
        </el-select>
        <el-select v-model="status" placeholder="状态" clearable @change="loadUsers">
          <el-option label="启用" value="active" />
          <el-option label="禁用" value="disabled" />
        </el-select>
        <el-button type="primary" @click="loadUsers">查询</el-button>
      </div>
    </div>

    <div class="card table-card">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="nickname" label="昵称" min-width="140">
          <template #default="{ row }">{{ row.nickname || "-" }}</template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="220" />
        <el-table-column prop="phone" label="手机号" min-width="140">
          <template #default="{ row }">{{ row.phone || "-" }}</template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="roleTagMap[row.role] || 'info'">{{ roleTextMap[row.role] || row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">{{ row.status === "active" ? "启用" : "禁用" }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
        <el-table-column prop="last_login_at" label="最近登录" min-width="180">
          <template #default="{ row }">{{ formatDate(row.last_login_at) }}</template>
        </el-table-column>
<el-table-column label="操作" fixed="right" width="300">
          <template #default="{ row }">
            <el-space>
              <el-button type="primary" link @click="toggleStatus(row)">
                {{ row.status === "active" ? "禁用" : "启用" }}
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
          @current-change="loadUsers"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { getUsersApi, resetUserPasswordApi, updateUserStatusApi, deleteUserApi } from "@/api/modules/business";
import { formatDate } from "@/utils";

const loading = ref(false);
const rows = ref<any[]>([]);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const keyword = ref("");
const role = ref("");
const status = ref("");

const roleTextMap: Record<string, string> = {
  user: "普通用户",
  staff: "员工",
  worker: "阿姨",
  admin: "管理员"
};

const roleTagMap: Record<string, "info" | "success" | "warning" | "danger"> = {
  user: "info",
  staff: "success",
  worker: "warning",
  admin: "danger"
};

const loadUsers = async () => {
  loading.value = true;
  try {
    const response = (await getUsersApi({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
      role: role.value || undefined,
      status: status.value || undefined
    })) as any;
    const data = response.data;
    rows.value = data.list;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
};

const toggleStatus = async (row: any) => {
  const nextStatus = row.status === "active" ? "disabled" : "active";
  await updateUserStatusApi(row.id, nextStatus);
  row.status = nextStatus;
  ElMessage.success(nextStatus === "active" ? "账号已启用" : "账号已禁用");
};

const resetPassword = async (row: any) => {
  const { value } = await ElMessageBox.prompt(`请为 ${row.email} 设置新密码`, "重置密码", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    inputPattern: /^.{6,}$/,
    inputErrorMessage: "密码长度不能少于 6 位"
  });
  await resetUserPasswordApi(row.id, value);
  ElMessage.success("密码已重置");
};

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm("确定要删除该用户吗？此操作不可恢复。", "删除确认", {
      confirmButtonText: "删除",
      cancelButtonText: "取消",
      type: "warning"
    });
    await deleteUserApi(row.id);
    ElMessage.success("删除成功");
    loadUsers();
  } catch (e) {
    if (e !== "cancel") {
      console.error(e);
    }
  }
};

onMounted(loadUsers);
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
  max-width: 340px;
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
