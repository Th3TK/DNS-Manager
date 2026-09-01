<script setup lang="ts">
defineOptions({
    inheritAttrs: false,
});

import { NCard, NLayout, NLayoutContent, NLayoutSider } from "naive-ui";

import AutoBreadcrumbs from "../components/AutoBreadcrumbs.vue";
import NavBar from "../components/NavBar.vue";
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
                <slot />
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
    box-sizing: border-box;
    display: flex !important;
    flex-direction: column;
}
</style>
