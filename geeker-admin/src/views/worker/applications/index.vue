<template>
  <div class="page">
    <div class="toolbar card">
      <div class="toolbar-left">
        <el-radio-group v-model="filters.status" @change="loadApplications">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="pending">待审核</el-radio-button>
          <el-radio-button label="approved">已通过</el-radio-button>
          <el-radio-button label="rejected">已拒绝</el-radio-button>
        </el-radio-group>
      </div>
      <el-button type="primary" @click="loadApplications">刷新</el-button>
    </div>

    <div class="card table-card">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="real_name" label="姓名" min-width="120" />
        <el-table-column prop="phone" label="手机号" min-width="140" />
        <el-table-column prop="gender" label="性别" width="100">
          <template #default="{ row }">
            {{ row.gender === "female" ? "女" : "男" }}
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="90" />
        <el-table-column prop="experience_years" label="经验" width="100">
          <template #default="{ row }">{{ row.experience_years }} 年</template>
        </el-table-column>
        <el-table-column label="技能" min-width="220">
          <template #default="{ row }">
            <el-space wrap>
              <el-tag v-for="skill in row.skills || []" :key="skill" size="small">{{ skill }}</el-tag>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTagMap[row.status]">{{ statusTextMap[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" min-width="180" />
        <el-table-column label="操作" fixed="right" width="220">
          <template #default="{ row }">
            <el-space>
              <el-button v-if="row.status === 'pending'" type="success" link @click="approve(row)">通过</el-button>
              <el-button v-if="row.status === 'pending'" type="danger" link @click="reject(row)">拒绝</el-button>
              <el-popover placement="left" trigger="click" width="320">
                <template #reference>
                  <el-button link>详情</el-button>
                </template>
                <div class="detail-popover">
                  <p><strong>地址：</strong>{{ row.address || "-" }}</p>
                  <p><strong>介绍：</strong>{{ row.introduction || "-" }}</p>
                  <p v-if="row.reject_reason"><strong>拒绝原因：</strong>{{ row.reject_reason }}</p>
                </div>
              </el-popover>
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
          @current-change="loadApplications"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts" name="workerApplications">
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { getApplicationsApi, reviewApplicationApi } from "@/api/modules/business";

const loading = ref(false);
const rows = ref<any[]>([]);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const filters = reactive({ status: "pending" });

const statusTextMap: Record<string, string> = {
  pending: "待审核",
  approved: "已通过",
  rejected: "已拒绝"
};

const statusTagMap: Record<string, "warning" | "success" | "danger"> = {
  pending: "warning",
  approved: "success",
  rejected: "danger"
};

const loadApplications = async () => {
  loading.value = true;
  try {
    const { data } = await getApplicationsApi({
      status: filters.status || undefined,
      page: page.value,
      page_size: pageSize.value
    });
    rows.value = data.list;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
};

const approve = async (row: any) => {
  await ElMessageBox.confirm(`确认通过 ${row.real_name} 的申请吗？`, "通过申请", { type: "warning" });
  await reviewApplicationApi(row.id, { status: "approved" });
  ElMessage.success("已通过申请");
  await loadApplications();
};

const reject = async (row: any) => {
  const { value } = await ElMessageBox.prompt(`请输入拒绝 ${row.real_name} 的原因`, "拒绝申请", {
    confirmButtonText: "确认",
    cancelButtonText: "取消",
    inputPattern: /.+/,
    inputErrorMessage: "请填写拒绝原因"
  });
  await reviewApplicationApi(row.id, { status: "rejected", reject_reason: value });
  ElMessage.success("已拒绝申请");
  await loadApplications();
};

onMounted(loadApplications);
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

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.detail-popover {
  color: var(--el-text-color-regular);
  line-height: 1.8;
}

.detail-popover p {
  margin: 0 0 8px;
}
</style>
