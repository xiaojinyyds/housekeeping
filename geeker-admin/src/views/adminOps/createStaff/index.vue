<template>
  <div class="page">
    <div class="card header-card">
      <div>
        <h2>新建员工账号</h2>
        <p>身份证号必填，可用于登录；登录邮箱改为选填，不填会自动生成内部账号。</p>
      </div>
      <el-button @click="router.push('/staff/list')">返回员工列表</el-button>
    </div>

    <div class="card form-card">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="staff-form">
        <div class="grid two">
          <el-form-item label="身份证号（登录账号）" prop="id_card">
            <el-input v-model="form.id_card" placeholder="请输入18位身份证号" />
          </el-form-item>
          <el-form-item label="初始密码" prop="password">
            <el-input v-model="form.password" type="password" show-password placeholder="请输入至少 6 位密码" />
          </el-form-item>
        </div>

        <div class="grid three">
          <el-form-item label="登录邮箱（选填）" prop="email">
            <el-input v-model="form.email" placeholder="可不填；填写时建议用真实邮箱" />
          </el-form-item>
          <el-form-item label="真实姓名" prop="real_name">
            <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
          </el-form-item>
          <el-form-item label="员工昵称" prop="nickname">
            <el-input v-model="form.nickname" placeholder="请输入员工昵称" />
          </el-form-item>
        </div>

        <div class="grid two">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="头像地址">
            <el-input v-model="form.avatar_url" placeholder="选填，填写头像图片 URL" />
          </el-form-item>
        </div>

        <el-form-item label="说明">
          <el-alert title="新建员工默认角色为 staff，可在员工列表中启用/禁用并重置密码。" type="info" :closable="false" />
        </el-form-item>

        <div class="actions">
          <el-button @click="resetForm">重置</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm">创建员工</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { createUserApi } from "@/api/modules/business";

const router = useRouter();
const formRef = ref<FormInstance>();
const submitting = ref(false);

const createDefaultForm = () => ({
  id_card: "",
  email: "",
  password: "",
  real_name: "",
  nickname: "",
  phone: "",
  avatar_url: ""
});

const form = reactive(createDefaultForm());

const rules: FormRules = {
  id_card: [
    { required: true, message: "请输入身份证号", trigger: "blur" },
    { min: 18, max: 18, message: "身份证号应为18位", trigger: "blur" }
  ],
  password: [
    { required: true, message: "请输入初始密码", trigger: "blur" },
    { min: 6, message: "密码长度至少 6 位", trigger: "blur" }
  ],
  email: [{ type: "email", message: "邮箱格式不正确", trigger: ["blur", "change"] }],
  real_name: [{ required: true, message: "请输入真实姓名", trigger: "blur" }],
  nickname: [{ required: true, message: "请输入员工昵称", trigger: "blur" }],
  phone: [{ required: true, message: "请输入手机号", trigger: "blur" }]
};

const resetForm = () => {
  Object.assign(form, createDefaultForm());
  formRef.value?.clearValidate();
};

const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  submitting.value = true;
  try {
    await createUserApi({
      id_card: form.id_card,
      email: form.email || undefined,
      password: form.password,
      real_name: form.real_name,
      nickname: form.nickname,
      phone: form.phone,
      avatar_url: form.avatar_url || undefined,
      role: "staff"
    });
    ElMessage.success("员工账号创建成功");
    resetForm();
  } finally {
    submitting.value = false;
  }
};
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
