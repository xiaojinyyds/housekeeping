<template>
  <StaffWorkbench v-if="isStaff" />
  <AdminWorkbench v-else />
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useUserStore } from "@/stores/modules/user";
import AdminWorkbench from "./components/AdminWorkbench.vue";
import StaffWorkbench from "./components/StaffWorkbench.vue";

const userStore = useUserStore();
const isStaff = computed(() => userStore.userInfo.role === "staff");
</script>
