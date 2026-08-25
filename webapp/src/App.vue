<script setup lang="ts">
import { computed, ref } from "vue";
import { darkTheme, lightTheme, NConfigProvider, NNotificationProvider } from "naive-ui";

const isDark = ref(true);

const theme = computed(() => (isDark.value ? darkTheme : lightTheme));

const themeOverrides = {
    common: {
        fontSize: "16px",
    },
};
</script>

<template>
    <NConfigProvider
        :theme="theme"
        :theme-overrides="themeOverrides"
    >
        <NNotificationProvider>
            <RouterView />
        </NNotificationProvider>
    </NConfigProvider>
</template>
