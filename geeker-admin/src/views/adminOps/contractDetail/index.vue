<template>
  <div class="page" v-loading="loading">
    <div class="card header-card">
      <div>
        <h2>合同详情</h2>
        <p>查看签约信息、阿姨安排和回访售后记录。</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="router.push('/contract/create')">新建合同</el-button>
        <el-button @click="router.push('/contract/list')">返回合同列表</el-button>
      </div>
    </div>

    <template v-if="detail">
      <div class="grid two">
        <div class="card section-card">
          <div class="section-title">合同信息</div>
          <div class="info-grid">
            <div class="info-item"><label>合同编号</label><span>{{ detail.contract_no || "-" }}</span></div>
            <div class="info-item"><label>合同状态</label><span>{{ statusTextMap[detail.status] || detail.status || "-" }}</span></div>
            <div class="info-item"><label>客户姓名</label><span>{{ detail.customer_name || "-" }}</span></div>
            <div class="info-item"><label>客户电话</label><span>{{ detail.customer_phone || "-" }}</span></div>
            <div class="info-item"><label>阿姨姓名</label><span>{{ detail.worker_name || "-" }}</span></div>
            <div class="info-item"><label>签单员工</label><span>{{ detail.broker_staff_name || "-" }}</span></div>
            <div class="info-item"><label>订单类型</label><span>{{ detail.service_type || "-" }}</span></div>
            <div class="info-item"><label>客户来源</label><span>{{ detail.customer_source || "-" }}</span></div>
            <div class="info-item"><label>合同日期</label><span>{{ detail.contract_date || "-" }}</span></div>
            <div class="info-item"><label>签约时间</label><span>{{ detail.sign_date || "-" }}</span></div>
            <div class="info-item"><label>上户时间</label><span>{{ detail.start_date || "-" }}</span></div>
            <div class="info-item"><label>到期时间</label><span>{{ detail.end_date || "-" }}</span></div>
            <div class="info-item"><label>实际结束时间</label><span>{{ detail.actual_end_date || "-" }}</span></div>
            <div class="info-item"><label>最近回访</label><span>{{ detail.latest_follow_up_at || "-" }}</span></div>
          </div>
          <div class="single-line">
            <label>服务地址</label>
            <span>{{ detail.service_address || "-" }}</span>
          </div>
          <div class="single-line">
            <label>需求说明</label>
            <span>{{ detail.demand_detail || "-" }}</span>
          </div>
          <div class="single-line">
            <label>备注</label>
            <span>{{ detail.remark || "-" }}</span>
          </div>
        </div>

        <div class="card section-card">
          <div class="section-title">金额信息</div>
          <div class="info-grid">
            <div class="info-item"><label>签单金额</label><span>{{ formatMoney(detail.contract_amount) }}</span></div>
            <div class="info-item"><label>实际收款</label><span>{{ formatMoney(detail.actual_received) }}</span></div>
            <div class="info-item"><label>折扣</label><span>{{ detail.discount_rate ?? "-" }}</span></div>
            <div class="info-item"><label>服务费</label><span>{{ formatMoney(detail.service_fee) }}</span></div>
            <div class="info-item"><label>转介绍费</label><span>{{ formatMoney(detail.referral_fee) }}</span></div>
            <div class="info-item"><label>阿姨工资标准值</label><span>{{ formatMoney(detail.worker_salary_amount) }}</span></div>
            <div class="info-item"><label>退款金额</label><span>{{ formatMoney(detail.refund_amount) }}</span></div>
            <div class="info-item"><label>退款原因</label><span>{{ detail.refund_reason || "-" }}</span></div>
          </div>
          <div class="single-line">
            <label>阿姨工资说明</label>
            <span>{{ detail.worker_salary_desc || "-" }}</span>
          </div>
          <div class="single-line">
            <label>换人说明</label>
            <span>{{ detail.replace_status || "-" }}</span>
          </div>
        </div>
      </div>

      <div class="grid two">
        <div class="card section-card">
          <div class="section-title">新增回访记录</div>
          <el-form :model="followForm" label-position="top">
            <div class="grid two-inner">
              <el-form-item label="回访类型">
                <el-select v-model="followForm.follow_type" placeholder="请选择回访类型">
                  <el-option label="1 天回访" value="d1" />
                  <el-option label="7 天回访" value="d7" />
                  <el-option label="30 天回访" value="d30" />
                  <el-option label="售后处理" value="after_sale" />
                  <el-option label="其他" value="other" />
                </el-select>
              </el-form-item>
              <el-form-item label="回访结果">
                <el-input v-model="followForm.result" placeholder="如：客户满意、需继续跟进" />
              </el-form-item>
            </div>
            <div class="grid two-inner">
              <el-form-item label="计划回访时间">
                <el-date-picker v-model="followForm.planned_at" type="datetime" placeholder="请选择时间" value-format="YYYY-MM-DDTHH:mm:ss" />
              </el-form-item>
              <el-form-item label="合同状态">
                <el-select v-model="followForm.status" placeholder="需要时同步调整合同状态">
                  <el-option label="待上户" value="pending_start" />
                  <el-option label="服务中" value="serving" />
                  <el-option label="已暂停" value="paused" />
                  <el-option label="已完成" value="completed" />
                  <el-option label="已终止" value="terminated" />
                  <el-option label="已退款" value="refunded" />
                </el-select>
              </el-form-item>
            </div>
            <el-form-item label="回访内容">
              <el-input v-model="followForm.content" type="textarea" :rows="4" placeholder="请输入这次回访、售后、换人沟通等详细内容" />
            </el-form-item>
            <el-form-item>
              <el-switch v-model="followForm.need_action" inline-prompt active-text="是" inactive-text="否" />
              <span class="switch-label">是否需要后续动作</span>
            </el-form-item>
            <div class="actions">
              <el-button type="primary" :loading="submitting" @click="submitFollowup">保存回访记录</el-button>
            </div>
          </el-form>
        </div>

        <div class="card section-card">
          <div class="section-title">回访记录</div>
          <div v-if="followups.length" class="timeline-list">
            <div v-for="item in followups" :key="item.id" class="timeline-item">
              <div class="timeline-header">
                <strong>{{ item.staff_name || "员工" }}</strong>
                <span>{{ item.followed_at || item.created_at || "-" }}</span>
              </div>
              <div class="timeline-meta">
                <span>类型：{{ followTypeTextMap[item.follow_type] || item.follow_type || "-" }}</span>
                <span>结果：{{ item.result || "-" }}</span>
              </div>
              <p>{{ item.content || "-" }}</p>
              <p v-if="item.need_action">需要继续处理</p>
            </div>
          </div>
          <div v-else class="empty-text">暂无回访记录</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { createContractFollowupApi, getContractDetailApi, getContractFollowupsApi } from "@/api/modules/business";

const route = useRoute();
const router = useRouter();
const contractId = String(route.params.contractId || "");
const loading = ref(false);
const submitting = ref(false);
const detail = ref<any>(null);
const followups = ref<any[]>([]);

const statusTextMap: Record<string, string> = {
  pending_start: "待上户",
  serving: "服务中",
  paused: "已暂停",
  completed: "已完成",
  terminated: "已终止",
  refunded: "已退款"
};

const followTypeTextMap: Record<string, string> = {
  d1: "1 天回访",
  d7: "7 天回访",
  d30: "30 天回访",
  after_sale: "售后处理",
  other: "其他"
};

const createDefaultFollowForm = () => ({
  follow_type: "other",
  result: "",
  planned_at: "",
  status: "",
  content: "",
  need_action: false
});

const followForm = reactive(createDefaultFollowForm());

const formatMoney = (value?: number | null) => {
  if (value === null || value === undefined) return "-";
  return Number(value).toFixed(2);
};

const loadDetail = async () => {
  if (!contractId) return;
  loading.value = true;
  try {
    const [detailResponse, followupResponse] = await Promise.all([
      getContractDetailApi(contractId),
      getContractFollowupsApi(contractId)
    ]);
    detail.value = (detailResponse as any)?.data ?? null;
    followups.value = Array.isArray((followupResponse as any)?.data) ? (followupResponse as any).data : [];
  } finally {
    loading.value = false;
  }
};

const submitFollowup = async () => {
  if (!followForm.content) {
    ElMessage.warning("请先填写回访内容");
    return;
  }
  submitting.value = true;
  try {
    await createContractFollowupApi(contractId, { ...followForm });
    ElMessage.success("回访记录保存成功");
    Object.assign(followForm, createDefaultFollowForm());
    await loadDetail();
  } finally {
    submitting.value = false;
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

.grid.two {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.grid.two-inner {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
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

.section-title {
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 700;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 18px;
}

.info-item,
.single-line {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.single-line {
  margin-top: 16px;
}

.info-item label,
.single-line label {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.switch-label {
  margin-left: 12px;
  color: var(--el-text-color-secondary);
}

.actions {
  display: flex;
  justify-content: flex-end;
}

.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.timeline-item {
  padding: 14px 16px;
  border-radius: 12px;
  background: #f7f9fb;
}

.timeline-header,
.timeline-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.timeline-meta {
  margin-top: 8px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.timeline-item p {
  margin: 10px 0 0;
  line-height: 1.7;
}

.empty-text {
  color: var(--el-text-color-secondary);
}

@media (max-width: 1200px) {
  .grid.two,
  .grid.two-inner,
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
