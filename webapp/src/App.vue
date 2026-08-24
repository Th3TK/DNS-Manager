<script setup lang="ts">
import { computed, ref } from "vue";
import { darkTheme, lightTheme, NConfigProvider } from "naive-ui";

const isDark = ref(true);

const theme = computed(() => (isDark.value ? darkTheme : lightTheme));
</script>

<template>
    <NConfigProvider :theme="theme">
        <RouterView />
    </NConfigProvider>
</template>
