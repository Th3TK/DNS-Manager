<script setup lang="ts">
defineOptions({
    inheritAttrs: false,
});

defineProps<{
    fillHeight?: boolean;
}>();

import { NCard, NLayout, NLayoutContent, NLayoutSider, NScrollbar } from "naive-ui";

import AutoBreadcrumbs from "../components/navigation/AutoBreadcrumbs.vue";
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
        <NLayoutContent content-class="content">
            <AutoBreadcrumbs />

            <NCard
                class="content-card"
                content-class="content-card-content"
                v-bind="$attrs"
            >
                <NScrollbar
                    class="content-scrollbar"
                    :content-class="`content-scrollbar-content ${fillHeight ? 'content-scrollbar-content-fill-height' : ''}`"
                >
                    <slot />
                </NScrollbar>
            </NCard>
            <slot name="portal" />
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

:deep(.content-card) {
    min-height: 0;
    flex: 1;
}

:deep(.content-card-content) {
    flex: 1;
    min-height: 0;
    box-sizing: border-box;
    display: flex !important;
    flex-direction: column;
    padding: var(--spacing-md) var(--spacing-sm) var(--spacing-md) var(--spacing-lg);
}

.content-scrollbar {
    height: 100%;
}

:deep(.content-scrollbar-content) {
    padding-right: var(--spacing-md);
}
:deep(.content-scrollbar-content-fill-height) {
    height: 100%;
}
</style>
