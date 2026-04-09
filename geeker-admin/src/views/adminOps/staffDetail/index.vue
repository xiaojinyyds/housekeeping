<template>
  <div class="page" v-loading="loading">
    <div class="card header-card">
      <div>
        <h2>员工详情</h2>
        <p>查看员工账号基础信息和后台使用状态。</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="router.push(`/staff/edit/${staffId}`)">编辑员工</el-button>
        <el-button @click="router.push('/staff/list')">返回员工列表</el-button>
      </div>
    </div>

    <div v-if="detail" class="card section-card">
      <div class="info-grid">
        <div class="info-item">
          <label>真实姓名</label><span>{{ detail.real_name || "-" }}</span>
        </div>
        <div class="info-item">
          <label>员工昵称</label><span>{{ detail.nickname || "-" }}</span>
        </div>
        <div class="info-item">
          <label>登录邮箱</label><span>{{ detail.email || "-" }}</span>
        </div>
        <div class="info-item">
          <label>手机号</label><span>{{ detail.phone || "-" }}</span>
        </div>
        <div class="info-item">
          <label>角色</label><span>{{ detail.role === "staff" ? "员工" : detail.role || "-" }}</span>
        </div>
        <div class="info-item">
          <label>状态</label>
          <el-tag :type="detail.status === 'active' ? 'success' : 'danger'">
            {{ detail.status === "active" ? "启用" : "禁用" }}
          </el-tag>
        </div>
        <div class="info-item">
          <label>创建时间</label><span>{{ detail.created_at || "-" }}</span>
        </div>
        <div class="info-item">
          <label>最近登录</label><span>{{ detail.last_login_at || "-" }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { getUserDetailApi } from "@/api/modules/business";

const route = useRoute();
const router = useRouter();
const staffId = String(route.params.staffId || "");
const loading = ref(false);
const detail = ref<any>(null);

const loadDetail = async () => {
  if (!staffId) return;
  loading.value = true;
  try {
    const response = (await getUserDetailApi(staffId)) as any;
    detail.value = response?.data ?? null;
  } catch {
    ElMessage.error("员工详情获取失败");
  } finally {
    loading.value = false;
  }
};

onMounted(loadDetail);
</script>

<style scoped lang="scss">
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.header-card,
.section-card {
  padding: 20px;
}

.header-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px 18px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item label {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

@media (max-width: 900px) {
  .header-card,
  .header-actions,
  .info-grid {
    flex-direction: column;
    grid-template-columns: 1fr;
    align-items: flex-start;
  }
}
</style>
