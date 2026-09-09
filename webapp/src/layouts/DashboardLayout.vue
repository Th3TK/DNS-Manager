<script setup lang="ts">
defineOptions({
    inheritAttrs: false,
});

import { NLayout, NLayoutContent, NLayoutSider } from "naive-ui";

import NavBar from "../components/navigation/NavBar.vue";
</script>

<template>
    <NLayout
        class="layout"
        has-sider
    >
        <NLayoutSider
            class="navbar"
            :width="240"
            bordered
        >
            <NavBar />
        </NLayoutSider>
        <NLayoutContent
            content-class="content"
            v-bind="$attrs"
        >
            <slot />
        </NLayoutContent>
    </NLayout>
</template>

<style scoped>
.layout {
    height: 100vh;
}

.content,
:deep(.content) {
    flex: 1;
    min-height: 0;

    box-sizing: border-box;
    display: flex !important;
    flex-direction: column;

    padding: var(--spacing-md);
    gap: var(--spacing-md);
}
</style>
