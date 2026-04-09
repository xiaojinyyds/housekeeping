<template>
  <div class="page" v-loading="loading">
    <div class="card header-card">
      <div>
        <h2>编辑客户线索</h2>
        <p>维护客户来源、需求、预算和当前线索状态。</p>
      </div>
      <div class="header-actions">
        <el-button @click="router.push(`/lead/detail/${leadId}`)">返回详情</el-button>
      </div>
    </div>

    <div class="card form-card">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="lead-form">
        <div class="grid three">
          <el-form-item label="客户称呼" prop="customer_name">
            <el-input v-model="form.customer_name" placeholder="请输入客户称呼" />
          </el-form-item>
          <el-form-item label="联系方式" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入联系方式" />
          </el-form-item>
          <el-form-item label="订单类型" prop="service_type">
            <el-select v-model="form.service_type" placeholder="请选择订单类型">
              <el-option label="住家保姆" value="住家保姆" />
              <el-option label="白班保姆" value="白班保姆" />
              <el-option label="住家育儿嫂" value="住家育儿嫂" />
              <el-option label="白班育儿嫂" value="白班育儿嫂" />
              <el-option label="钟点工" value="钟点工" />
              <el-option label="月嫂" value="月嫂" />
              <el-option label="护工" value="护工" />
            </el-select>
          </el-form-item>
        </div>

        <div class="grid three">
          <el-form-item label="客户来源">
            <el-input v-model="form.source" placeholder="如：线索、转介绍、公海" />
          </el-form-item>
          <el-form-item label="来源补充">
            <el-input v-model="form.source_detail" placeholder="如：高老师、二次流转" />
          </el-form-item>
          <el-form-item label="线索名称">
            <el-input v-model="form.lead_name" placeholder="请输入线索名称或平台昵称" />
          </el-form-item>
        </div>

        <el-form-item label="需求地址">
          <el-input v-model="form.demand_address" placeholder="请输入需求地址" />
        </el-form-item>

        <el-form-item label="需求详情">
          <el-input v-model="form.demand_detail" type="textarea" :rows="4" placeholder="请输入客户需求详情" />
        </el-form-item>

        <div class="grid three">
          <el-form-item label="线索日期" prop="lead_date">
            <el-date-picker v-model="form.lead_date" type="date" value-format="YYYY-MM-DD" class="full-width" />
          </el-form-item>
          <el-form-item label="预算">
            <el-input-number v-model="form.budget" :min="0" :precision="2" class="full-width" />
          </el-form-item>
          <el-form-item label="线索类别">
            <el-select v-model="form.lead_category" placeholder="请选择线索类别">
              <el-option label="A类" value="A" />
              <el-option label="B类" value="B" />
            </el-select>
          </el-form-item>
          <el-form-item label="线索状态">
            <el-select v-model="form.status" placeholder="请选择线索状态">
              <el-option label="新线索" value="new" />
              <el-option label="跟进中" value="contacting" />
              <el-option label="面试中" value="interviewing" />
              <el-option label="已签约" value="signed" />
              <el-option label="已关闭" value="closed" />
              <el-option label="无效" value="invalid" />
            </el-select>
          </el-form-item>
        </div>

        <el-form-item v-if="form.status === 'invalid'" label="无效原因">
          <el-input v-model="form.invalid_reason" placeholder="请输入无效原因" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>

        <div class="actions">
          <el-button @click="loadDetail">重置为服务器数据</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm">保存线索</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { getLeadDetailApi, updateLeadApi } from "@/api/modules/business";

const route = useRoute();
const router = useRouter();
const leadId = String(route.params.leadId || "");
const formRef = ref<FormInstance>();
const loading = ref(false);
const submitting = ref(false);

const createDefaultForm = () => ({
  customer_name: "",
  phone: "",
  service_type: "",
  source: "",
  source_detail: "",
  lead_name: "",
  demand_address: "",
  demand_detail: "",
  lead_date: "",
  budget: undefined as number | undefined,
  lead_category: "B",
  status: "new",
  invalid_reason: "",
  remark: ""
});

const form = reactive(createDefaultForm());

const rules: FormRules = {
  customer_name: [{ required: true, message: "请输入客户称呼", trigger: "blur" }],
  phone: [{ required: true, message: "请输入联系方式", trigger: "blur" }],
  service_type: [{ required: true, message: "请选择订单类型", trigger: "change" }],
  lead_date: [{ required: true, message: "请选择线索日期", trigger: "change" }]
};

const loadDetail = async () => {
  if (!leadId) return;
  loading.value = true;
  try {
    const response = (await getLeadDetailApi(leadId)) as any;
    const data = response?.data ?? {};
    Object.assign(form, {
      customer_name: data.customer_name || "",
      phone: data.phone || "",
      service_type: data.service_type || "",
      source: data.source || "",
      source_detail: data.source_detail || "",
      lead_name: data.lead_name || "",
      demand_address: data.demand_address || "",
      demand_detail: data.demand_detail || "",
      lead_date: data.lead_date || "",
      budget: data.budget ?? undefined,
      lead_category: data.lead_category || "B",
      status: data.status || "new",
      invalid_reason: data.invalid_reason || "",
      remark: data.remark || ""
    });
    formRef.value?.clearValidate();
  } finally {
    loading.value = false;
  }
};

const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  submitting.value = true;
  try {
    await updateLeadApi(leadId, { ...form });
    ElMessage.success("客户线索更新成功");
    router.push({ path: `/lead/detail/${leadId}`, query: { refresh: Date.now().toString() } });
  } finally {
    submitting.value = false;
  }
};

loadDetail();
</script>

<style scoped lang="scss">
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.header-card,
.form-card {
  padding: 20px;
}

.header-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.header-card h2 {
  margin: 0 0 6px;
  font-size: 22px;
}

.header-card p {
  margin: 0;
  color: var(--el-text-color-secondary);
}

.grid {
  display: grid;
  gap: 16px;
}

.grid.three {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.full-width {
  width: 100%;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 900px) {
  .grid.three,
  .header-card {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
