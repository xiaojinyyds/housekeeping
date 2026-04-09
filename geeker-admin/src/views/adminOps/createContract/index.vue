<template>
  <div class="page">
    <div class="card header-card">
      <div>
        <h2>新建合同</h2>
        <p>必须先关联线索，签单员工自动识别为当前登录账号。</p>
      </div>
      <el-button @click="router.push('/contract/list')">返回合同列表</el-button>
    </div>

    <div class="card form-card">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <div class="grid three">
          <el-form-item label="关联线索" prop="lead_id">
            <el-select v-model="form.lead_id" filterable placeholder="必选：搜索并关联线索" @change="handleLeadChange">
              <el-option
                v-for="item in leadOptions"
                :key="item.id"
                :label="`${item.customer_name || '客户'} / ${item.phone || '-'} / ${item.lead_no || ''}`"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="签单员工">
            <el-input :model-value="currentUserName" disabled />
          </el-form-item>
          <el-form-item label="合同日期" prop="contract_date">
            <el-date-picker v-model="form.contract_date" type="date" value-format="YYYY-MM-DD" placeholder="请选择合同日期" />
          </el-form-item>
        </div>

        <div class="grid three">
          <el-form-item label="客户姓名" prop="customer_name">
            <el-input v-model="form.customer_name" placeholder="请输入客户姓名" />
          </el-form-item>
          <el-form-item label="客户电话" prop="customer_phone">
            <el-input v-model="form.customer_phone" placeholder="请输入客户电话" />
          </el-form-item>
          <el-form-item label="客户来源">
            <el-input v-model="form.customer_source" placeholder="如：转介绍、地推、老客户复购" />
          </el-form-item>
        </div>

        <div class="grid two">
          <el-form-item label="服务地址" prop="service_address">
            <el-input v-model="form.service_address" placeholder="请输入服务地址" />
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
          <el-form-item label="阿姨档案" prop="worker_user_id">
            <el-select v-model="form.worker_user_id" filterable placeholder="请选择阿姨档案">
              <el-option
                v-for="item in workerOptions"
                :key="item.user_id || item.id"
                :label="`${item.real_name || '阿姨'} / ${item.phone || '-'}`"
                :value="item.user_id || item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="签约时间">
            <el-date-picker v-model="form.sign_date" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="请选择签约时间" />
          </el-form-item>
          <el-form-item label="上户时间">
            <el-date-picker v-model="form.start_date" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="请选择上户时间" />
          </el-form-item>
        </div>

        <div class="grid three">
          <el-form-item label="到期时间">
            <el-date-picker v-model="form.end_date" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="请选择到期时间" />
          </el-form-item>
          <el-form-item label="合同状态">
            <el-select v-model="form.status" placeholder="请选择合同状态">
              <el-option label="待上户" value="pending_start" />
              <el-option label="服务中" value="serving" />
              <el-option label="已暂停" value="paused" />
              <el-option label="已完成" value="completed" />
              <el-option label="已终止" value="terminated" />
              <el-option label="已退款" value="refunded" />
            </el-select>
          </el-form-item>
          <el-form-item label="签单金额">
            <el-input-number v-model="form.contract_amount" :min="0" :precision="2" class="full-width" />
          </el-form-item>
        </div>

        <div class="grid two">
          <el-form-item label="实收金额">
            <el-input-number v-model="form.actual_received" :min="0" :precision="2" class="full-width" />
          </el-form-item>
          <el-form-item label="需求说明">
            <el-input v-model="form.demand_detail" type="textarea" :rows="3" placeholder="请输入需求说明" />
          </el-form-item>
        </div>

        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>

        <div class="actions">
          <el-button @click="resetForm">重置</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm">创建合同</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { createContractApi, getLeadListApi, getWorkersApi } from "@/api/modules/business";
import { useUserStore } from "@/stores/modules/user";

const router = useRouter();
const userStore = useUserStore();
const currentUserName = computed(
  () => userStore.userInfo?.real_name || userStore.userInfo?.name || userStore.userInfo?.nickname || "当前登录账号"
);

const formRef = ref<FormInstance>();
const submitting = ref(false);
const leadOptions = ref<any[]>([]);
const workerOptions = ref<any[]>([]);

const createDefaultForm = () => ({
  lead_id: "",
  contract_date: "",
  customer_name: "",
  customer_phone: "",
  customer_source: "",
  service_address: "",
  service_type: "",
  worker_user_id: "",
  sign_date: "",
  start_date: "",
  end_date: "",
  status: "pending_start",
  contract_amount: undefined as number | undefined,
  actual_received: undefined as number | undefined,
  demand_detail: "",
  remark: ""
});

const form = reactive(createDefaultForm());

const rules: FormRules = {
  lead_id: [{ required: true, message: "请选择关联线索", trigger: "change" }],
  contract_date: [{ required: true, message: "请选择合同日期", trigger: "change" }],
  customer_name: [{ required: true, message: "请输入客户姓名", trigger: "blur" }],
  customer_phone: [{ required: true, message: "请输入客户电话", trigger: "blur" }],
  service_address: [{ required: true, message: "请输入服务地址", trigger: "blur" }],
  service_type: [{ required: true, message: "请选择订单类型", trigger: "change" }],
  worker_user_id: [{ required: true, message: "请选择阿姨档案", trigger: "change" }]
};

const resetForm = () => {
  Object.assign(form, createDefaultForm());
  formRef.value?.clearValidate();
};

const handleLeadChange = (leadId: string) => {
  const lead = leadOptions.value.find(item => item.id === leadId);
  if (!lead) return;
  form.customer_name = form.customer_name || lead.customer_name || "";
  form.customer_phone = form.customer_phone || lead.phone || "";
  form.customer_source = form.customer_source || lead.source_detail || lead.source || "";
  form.service_type = form.service_type || lead.service_type || "";
  form.service_address = form.service_address || lead.demand_address || "";
  form.demand_detail = form.demand_detail || lead.demand_detail || "";
};

const loadOptions = async () => {
  const [leadResponse, workerResponse] = await Promise.allSettled([
    getLeadListApi({ page: 1, page_size: 100 }),
    getWorkersApi({ page: 1, page_size: 100 })
  ]);

  leadOptions.value =
    leadResponse.status === "fulfilled" && Array.isArray((leadResponse.value as any)?.data?.list)
      ? (leadResponse.value as any).data.list
      : [];

  workerOptions.value =
    workerResponse.status === "fulfilled" && Array.isArray((workerResponse.value as any)?.data?.list)
      ? (workerResponse.value as any).data.list
      : [];
};

const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  submitting.value = true;
  try {
    await createContractApi({ ...form });
    ElMessage.success("合同创建成功");
    router.push({ path: "/contract/list", query: { refresh: Date.now().toString() } });
  } finally {
    submitting.value = false;
  }
};

onMounted(loadOptions);
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

.grid.two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
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
  .header-card,
  .grid.two,
  .grid.three {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
