<template>
  <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" size="large">
    <el-form-item prop="username">
      <el-input v-model="loginForm.username" placeholder="请输入邮箱或手机号">
        <template #prefix>
          <el-icon class="el-input__icon">
            <User />
          </el-icon>
        </template>
      </el-input>
    </el-form-item>
    <el-form-item prop="password">
      <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password autocomplete="current-password">
        <template #prefix>
          <el-icon class="el-input__icon">
            <Lock />
          </el-icon>
        </template>
      </el-input>
    </el-form-item>
  </el-form>
  <div class="login-btn">
    <el-button :icon="CircleClose" round size="large" @click="resetForm(loginFormRef)">重置</el-button>
    <el-button :icon="UserFilled" round size="large" type="primary" :loading="loading" @click="login(loginFormRef)">登录</el-button>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import type { ElForm } from "element-plus";
import { ElMessage, ElNotification } from "element-plus";
import { CircleClose, Lock, User, UserFilled } from "@element-plus/icons-vue";
import { HOME_URL } from "@/config";
import { Login } from "@/api/interface";
import { getProfileApi, loginApi } from "@/api/modules/login";
import { initDynamicRouter } from "@/routers/modules/dynamicRouter";
import { useKeepAliveStore } from "@/stores/modules/keepAlive";
import { useTabsStore } from "@/stores/modules/tabs";
import { useUserStore } from "@/stores/modules/user";

type FormInstance = InstanceType<typeof ElForm>;

const router = useRouter();
const userStore = useUserStore();
const tabsStore = useTabsStore();
const keepAliveStore = useKeepAliveStore();

const loginFormRef = ref<FormInstance>();
const loading = ref(false);

const loginRules = reactive({
  username: [{ required: true, message: "请输入账号", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }]
});

const loginForm = reactive<Login.ReqLoginForm>({
  username: "",
  password: ""
});

const login = (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  formEl.validate(async valid => {
    if (!valid) return;
    loading.value = true;
    try {
      const { data } = await loginApi(loginForm);
      userStore.setToken(data.access_token);

      const profileRes = await getProfileApi();
      const profile = profileRes.data;

      if (!profile || !["admin", "staff"].includes(profile.role)) {
        userStore.setToken("");
        userStore.setUserInfo({ name: "" });
        ElMessage.error("该账号没有后台访问权限");
        return;
      }

      userStore.setUserInfo({
        id: profile.id,
        name: profile.nickname || profile.email || "后台用户",
        email: profile.email,
        phone: profile.phone,
        role: profile.role,
        nickname: profile.nickname,
        avatar_url: profile.avatar_url
      });

      await initDynamicRouter();
      tabsStore.setTabs([]);
      keepAliveStore.setKeepAliveName([]);
      router.push(HOME_URL);

      ElNotification({
        title: "登录成功",
        message: `欢迎回来，${profile.nickname || profile.email}`,
        type: "success",
        duration: 2500
      });
    } finally {
      loading.value = false;
    }
  });
};

const resetForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  formEl.resetFields();
};

onMounted(() => {
  document.onkeydown = (e: KeyboardEvent) => {
    if (e.code === "Enter" || e.code === "NumpadEnter") {
      if (loading.value) return;
      login(loginFormRef.value);
    }
  };
});

onBeforeUnmount(() => {
  document.onkeydown = null;
});
</script>

<style scoped lang="scss">
@import "../index.scss";
</style>
