<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { darkTheme, lightTheme, NConfigProvider, NNotificationProvider } from "naive-ui";
import { useAuthenticationStore } from "./stores/useAuthenticationStore";
import { useRecordsStatusStore } from "./stores/useRecordsStatusStore";

const isDark = ref(true);

const theme = computed(() => (isDark.value ? darkTheme : lightTheme));

const themeOverrides = {
    common: {
        fontSize: "16px",
        fontFamily: "Lato",
        fontFamilyMono: "Fira Code",
        fontWeightStrong: "600",
    },
};

const authentication = useAuthenticationStore();
const recordsStatus = useRecordsStatusStore();

onMounted(() => {
    authentication.refresh();
    recordsStatus.connect();
});
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
