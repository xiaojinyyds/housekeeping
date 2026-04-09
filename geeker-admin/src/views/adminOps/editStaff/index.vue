<template>
  <div class="page" v-loading="loading">
    <div class="card header-card">
      <div>
        <h2>编辑员工</h2>
        <p>维护员工姓名、昵称、手机号和头像等账号信息。</p>
      </div>
      <el-button @click="router.push(`/staff/detail/${staffId}`)">返回详情</el-button>
    </div>

    <div class="card form-card">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <div class="grid three">
          <el-form-item label="真实姓名" prop="real_name">
            <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
          </el-form-item>
          <el-form-item label="员工昵称" prop="nickname">
            <el-input v-model="form.nickname" placeholder="请输入员工昵称" />
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入手机号" />
          </el-form-item>
        </div>

        <el-form-item label="头像地址">
          <el-input v-model="form.avatar_url" placeholder="选填，填写头像图片 URL" />
        </el-form-item>

        <div class="actions">
          <el-button @click="loadDetail">重置为服务器数据</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm">保存员工信息</el-button>
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
import { getUserDetailApi, updateUserInfoApi } from "@/api/modules/business";

const route = useRoute();
const router = useRouter();
const staffId = String(route.params.staffId || "");
const formRef = ref<FormInstance>();
const loading = ref(false);
const submitting = ref(false);

const form = reactive({
  real_name: "",
  nickname: "",
  phone: "",
  avatar_url: ""
});

const rules: FormRules = {
  real_name: [{ required: true, message: "请输入真实姓名", trigger: "blur" }],
  nickname: [{ required: true, message: "请输入员工昵称", trigger: "blur" }],
  phone: [{ required: true, message: "请输入手机号", trigger: "blur" }]
};

const loadDetail = async () => {
  if (!staffId) return;
  loading.value = true;
  try {
    const response = (await getUserDetailApi(staffId)) as any;
    const data = response?.data ?? {};
    form.real_name = data.real_name || "";
    form.nickname = data.nickname || "";
    form.phone = data.phone || "";
    form.avatar_url = data.avatar_url || "";
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
    await updateUserInfoApi(staffId, { ...form });
    ElMessage.success("员工信息更新成功");
    router.push(`/staff/detail/${staffId}`);
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

.grid.three {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 900px) {
  .header-card,
  .grid.three {
    flex-direction: column;
    grid-template-columns: 1fr;
    align-items: flex-start;
  }
}
</style>
