<template>
  <div class="page">
    <div class="toolbar card">
      <el-input v-model="keyword" placeholder="搜索姓名或手机号" clearable class="search-input" @keyup.enter="loadWorkers" />
      <div class="toolbar-right">
        <el-select v-model="availability" placeholder="接单状态" clearable @change="loadWorkers">
          <el-option label="可接单" :value="true" />
          <el-option label="休息中" :value="false" />
        </el-select>
        <el-button type="primary" @click="loadWorkers">查询</el-button>
      </div>
    </div>

    <div class="card table-card">
      <el-table :data="rows" v-loading="loading">
        <el-table-column prop="real_name" label="姓名" min-width="120" />
        <el-table-column prop="phone" label="手机号" min-width="140" />
        <el-table-column prop="age" label="年龄" width="90" />
        <el-table-column label="经验" width="100">
          <template #default="{ row }">{{ row.experience_years || 0 }} 年</template>
        </el-table-column>
        <el-table-column label="评分" width="100">
          <template #default="{ row }">{{ row.rating || 0 }}</template>
        </el-table-column>
        <el-table-column label="完成订单" width="110">
          <template #default="{ row }">{{ row.completed_orders || 0 }}</template>
        </el-table-column>
        <el-table-column label="技能" min-width="220">
          <template #default="{ row }">
            <el-space wrap>
              <el-tag v-for="skill in row.skills || []" :key="skill" size="small" effect="plain">{{ skill }}</el-tag>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="140">
          <template #default="{ row }">
            <el-tag :type="row.is_available ? 'success' : 'info'">{{ row.is_available ? "可接单" : "休息中" }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="推荐" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_recommended ? 'warning' : 'info'">{{ row.is_recommended ? "首页推荐" : "普通" }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="240">
          <template #default="{ row }">
            <el-space>
              <el-switch :model-value="row.is_available" inline-prompt active-text="开" inactive-text="关" @change="toggleAvailable(row)" />
              <el-button type="warning" link @click="toggleRecommend(row)">
                {{ row.is_recommended ? "取消推荐" : "设为推荐" }}
              </el-button>
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

<script setup lang="ts" name="workerList">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { getWorkersApi, updateWorkerAvailableApi, updateWorkerRecommendApi } from "@/api/modules/business";

const loading = ref(false);
const rows = ref<any[]>([]);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const keyword = ref("");
const availability = ref<boolean | undefined>();

const loadWorkers = async () => {
  loading.value = true;
  try {
    const { data } = await getWorkersApi({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
      is_available: availability.value
    });
    rows.value = data.list;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
};

const toggleAvailable = async (row: any) => {
  await updateWorkerAvailableApi(row.id, !row.is_available);
  row.is_available = !row.is_available;
  ElMessage.success(row.is_available ? "已开启接单" : "已暂停接单");
};

const toggleRecommend = async (row: any) => {
  await updateWorkerRecommendApi(row.id, !row.is_recommended);
  row.is_recommended = !row.is_recommended;
  ElMessage.success(row.is_recommended ? "已设为首页推荐" : "已取消推荐");
};

onMounted(loadWorkers);
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
  max-width: 320px;
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
  .toolbar {
    flex-direction: column;
  }

  .toolbar-right {
    flex-direction: column;
  }
}
</style>
