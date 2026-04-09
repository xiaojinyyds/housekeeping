<template>
  <div class="page" v-loading="loading">
    <div class="card header-card">
      <div>
        <h2>线索详情</h2>
        <p>查看客户需求，并持续补充跟进记录。</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="router.push(`/lead/edit/${route.params.leadId}`)">编辑线索</el-button>
        <el-button @click="router.push('/lead/list')">返回线索列表</el-button>
      </div>
    </div>

    <template v-if="detail">
      <div class="grid two">
        <div class="card section-card">
          <div class="section-title">线索信息</div>
          <div class="info-grid">
            <div class="info-item"><label>客户称呼</label><span>{{ detail.customer_name || "-" }}</span></div>
            <div class="info-item"><label>联系方式</label><span>{{ detail.phone || "-" }}</span></div>
            <div class="info-item"><label>客户来源</label><span>{{ detail.source_detail || detail.source || "-" }}</span></div>
            <div class="info-item"><label>线索名称</label><span>{{ detail.lead_name || "-" }}</span></div>
            <div class="info-item"><label>线索日期</label><span>{{ detail.lead_date || "-" }}</span></div>
            <div class="info-item"><label>订单类型</label><span>{{ detail.service_type || "-" }}</span></div>
            <div class="info-item"><label>跟进人</label><span>{{ detail.owner_staff_name || "-" }}</span></div>
            <div class="info-item"><label>状态</label><span>{{ statusTextMap[detail.status] || detail.status || "-" }}</span></div>
            <div class="info-item"><label>线索类别</label><span>{{ detail.lead_category ? `${detail.lead_category}类` : "-" }}</span></div>
          </div>
          <div class="single-line">
            <label>需求地址</label>
            <span>{{ detail.demand_address || "-" }}</span>
          </div>
          <div class="single-line">
            <label>需求详情</label>
            <span>{{ detail.demand_detail || "-" }}</span>
          </div>
          <div class="single-line">
            <label>备注</label>
            <span>{{ detail.remark || "-" }}</span>
          </div>
        </div>

        <div class="card section-card">
          <div class="section-title">新增跟进记录</div>
          <el-form ref="formRef" :model="followForm" label-position="top">
            <el-form-item label="跟进方式">
              <el-select v-model="followForm.follow_type" placeholder="请选择跟进方式">
                <el-option label="电话" value="phone" />
                <el-option label="微信" value="wechat" />
                <el-option label="到访" value="visit" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
            <el-form-item label="跟进结果">
              <el-input v-model="followForm.follow_result" placeholder="如：未接通、满意、不需要" />
            </el-form-item>
            <el-form-item label="线索状态">
              <el-select v-model="followForm.status" placeholder="请选择线索状态">
                <el-option label="新线索" value="new" />
                <el-option label="跟进中" value="contacting" />
                <el-option label="面试中" value="interviewing" />
                <el-option label="已签约" value="signed" />
                <el-option label="已关闭" value="closed" />
                <el-option label="无效" value="invalid" />
              </el-select>
            </el-form-item>
            <el-form-item label="跟进内容">
              <el-input v-model="followForm.content" type="textarea" :rows="4" placeholder="请输入这次跟进的详细内容" />
            </el-form-item>
            <el-form-item label="下一步动作">
              <el-input v-model="followForm.next_action" placeholder="如：明天下午继续电话跟进" />
            </el-form-item>
            <div class="actions">
              <el-button type="primary" :loading="submitting" @click="submitFollowRecord">保存跟进记录</el-button>
            </div>
          </el-form>
        </div>
      </div>

      <div class="card section-card">
        <div class="section-title">跟进记录</div>
        <div v-if="followRecords.length" class="timeline-list">
          <div v-for="item in followRecords" :key="item.id" class="timeline-item">
            <div class="timeline-header">
              <strong>{{ item.staff_name || "员工" }}</strong>
              <span>{{ item.created_at || "-" }}</span>
            </div>
            <div class="timeline-meta">
              <span>方式：{{ followTypeTextMap[item.follow_type] || item.follow_type || "-" }}</span>
              <span>结果：{{ item.follow_result || "-" }}</span>
            </div>
            <p>{{ item.content || "-" }}</p>
            <p v-if="item.next_action">下一步：{{ item.next_action }}</p>
          </div>
        </div>
        <div v-else class="empty-text">暂无跟进记录</div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { createLeadFollowRecordApi, getLeadDetailApi, getLeadFollowRecordsApi } from "@/api/modules/business";

const route = useRoute();
const router = useRouter();
const leadId = String(route.params.leadId || "");
const loading = ref(false);
const submitting = ref(false);
const detail = ref<any>(null);
const followRecords = ref<any[]>([]);

const statusTextMap: Record<string, string> = {
  new: "新线索",
  contacting: "跟进中",
  interviewing: "面试中",
  signed: "已签约",
  closed: "已关闭",
  invalid: "无效"
};

const followTypeTextMap: Record<string, string> = {
  phone: "电话",
  wechat: "微信",
  visit: "到访",
  other: "其他"
};

const createDefaultFollowForm = () => ({
  follow_type: "phone",
  follow_result: "",
  status: "contacting",
  content: "",
  next_action: ""
});

const followForm = reactive(createDefaultFollowForm());

const loadDetail = async () => {
  if (!leadId) return;
  loading.value = true;
  try {
    const [detailResponse, recordResponse] = await Promise.all([
      getLeadDetailApi(leadId),
      getLeadFollowRecordsApi(leadId)
    ]);
    detail.value = (detailResponse as any)?.data ?? null;
    followRecords.value = Array.isArray((recordResponse as any)?.data) ? (recordResponse as any).data : [];
    followForm.status = detail.value?.status || "contacting";
  } finally {
    loading.value = false;
  }
};

const submitFollowRecord = async () => {
  if (!followForm.content) {
    ElMessage.warning("请先填写跟进内容");
    return;
  }
  submitting.value = true;
  try {
    await createLeadFollowRecordApi(leadId, { ...followForm });
    ElMessage.success("跟进记录保存成功");
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
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
