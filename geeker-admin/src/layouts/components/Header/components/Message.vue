<template>
  <div class="message">
    <el-popover placement="bottom" :width="320" trigger="click" @show="loadPending">
      <template #reference>
        <el-badge :value="pendingCount > 0 ? pendingCount : ''" :hidden="pendingCount <= 0" class="item">
          <i :class="'iconfont icon-xiaoxi'" class="toolBar-icon"></i>
        </el-badge>
      </template>
      <div class="message-panel">
        <div class="panel-title">待跟进预约留言</div>
        <div v-if="pendingCount > 0" class="pending-tip">
          您有 <strong>{{ pendingCount }}</strong> 条未读待跟进客户留言
        </div>
        <div v-else class="message-empty">暂无待跟进留言</div>
        <el-button v-if="pendingCount > 0" type="primary" link @click="goGuestLeads">前往处理</el-button>
      </div>
    </el-popover>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { getGuestLeadPendingCountApi } from "@/api/modules/business";
import { useUserStore } from "@/stores/modules/user";

const router = useRouter();
const userStore = useUserStore();
const pendingCount = ref(0);

const loadPending = async () => {
  const role = userStore.userInfo?.role;
  if (!role || !["admin", "staff"].includes(role)) {
    pendingCount.value = 0;
    return;
  }
  try {
    const response = (await getGuestLeadPendingCountApi()) as any;
    const data = response?.data ?? response ?? {};
    pendingCount.value = Number(data.pending_count || 0);
  } catch {
    pendingCount.value = 0;
  }
};

const goGuestLeads = () => {
  router.push("/lead/guest");
};

onMounted(loadPending);
</script>

<style scoped lang="scss">
.message-panel {
  padding: 8px 4px;
}
.panel-title {
  font-weight: 600;
  margin-bottom: 12px;
}
.pending-tip {
  margin-bottom: 12px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
}
.message-empty {
  color: var(--el-text-color-secondary);
  margin-bottom: 12px;
}
</style>
