<script setup lang="ts">
import Provider from './ui/provider/index.vue'

const route = useRoute()

const settingsStore = useSettingsStore()
const keepAliveStore = useKeepAliveStore()

const { auth } = useAuth()

const isAuth = computed(() => {
  return route.matched.every((item) => {
    return item.meta.auth ? (item.meta.auth === true ? true : auth(item.meta.auth)) : true
  })
})

watch([
  () => settingsStore.settings.app.enableDynamicTitle,
  () => settingsStore.title,
], () => {
  nextTick(() => {
    if (settingsStore.settings.app.enableDynamicTitle && settingsStore.title) {
      document.title = settingsStore.title ?? import.meta.env.VITE_APP_TITLE
    }
    else {
      document.title = import.meta.env.VITE_APP_TITLE
    }
  })
}, {
  immediate: true,
  deep: true,
})
</script>

<template>
  <Provider>
    <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in" appear>
        <KeepAlive :include="keepAliveStore.list">
          <component :is="Component" v-if="isAuth" :key="route.fullPath" />
          <FmNotAllowed v-else />
        </KeepAlive>
      </Transition>
    </RouterView>
    <FmToast />
  </Provider>
</template>

<style scoped>
.navbar-enter-active,
.navbar-leave-active {
  transition: transform 0.15s ease-in-out;
}

.navbar-enter-from,
.navbar-leave-to {
  transform: translateY(-100%);
}

.tabbar-enter-active,
.tabbar-leave-active {
  transition: transform 0.15s ease-in-out;
}

.tabbar-enter-from,
.tabbar-leave-to {
  transform: translateY(100%);
}

/* 主内容区动画 */
.fade-enter-active {
  transition: 0.2s;
}

.fade-leave-active {
  transition: 0.15s;
}

.fade-enter-from {
  opacity: 0;
}

.fade-leave-to {
  opacity: 0;
}
</style>
