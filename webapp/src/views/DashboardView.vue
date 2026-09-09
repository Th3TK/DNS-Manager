<script setup lang="ts">
import { NGrid, NGridItem } from "naive-ui";
import DashboardLayout from "../layouts/DashboardLayout.vue";
import DashboardRecordStatusCard from "../components/display/DashboardRecordStatusCard.vue";
import DashboardDependencyStatusCard from "../components/display/DashboardDependencyStatusCard.vue";
import DashboardNameSearchCard from "../components/display/DashboardNameSearchCard.vue";
</script>

<template>
    <DashboardLayout>
        <NGrid
            :cols="2"
            :x-gap="16"
            :y-gap="16"
            class="grid"
        >
            <NGridItem>
                <DashboardDependencyStatusCard class="content-card" />
            </NGridItem>

            <NGridItem>
                <DashboardRecordStatusCard class="content-card" />
            </NGridItem>

            <NGridItem :span="2">
                <DashboardNameSearchCard class="content-card" />
            </NGridItem>
        </NGrid>
    </DashboardLayout>
</template>

<style lang="css" scoped>
.grid {
    height: 100%;
    box-sizing: border-box;
    grid-template-rows: auto 1fr;
}
:deep(.content-card) {
    height: 100%;
    box-sizing: border-box;
}
:deep(.dashboard-card-title) {
    margin: var(--spacing-xs) 0;
}

:deep(.dashboard-card-header) {
    align-items: start;
    flex-wrap: nowrap !important;
}

:deep(.big-text) {
    font-size: 18px;
}
:deep(.medium-text) {
    font-size: 16px;
}

:deep(.small-text) {
    font-size: 14px;
}
</style>
