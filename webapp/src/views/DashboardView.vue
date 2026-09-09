<script setup lang="ts">
import { NCard, NFlex, NGrid, NGridItem, NIcon, NPopover, NText, useThemeVars } from "naive-ui";
import DashboardLayout from "../layouts/DashboardLayout.vue";
import { Help } from "@vicons/tabler";
import NameSearchTable from "../components/tables/name-search/NameSearchTable.vue";
import DashboardRecordStatusCard from "../components/display/DashboardRecordStatusCard.vue";
import DashboardDependencyStatusCard from "../components/display/DashboardDependencyStatusCard.vue";

const theme = useThemeVars();
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
                <NCard class="content-card">
                    <template #header>
                        <NFlex class="dashboard-card-header">
                            <NFlex
                                vertical
                                :size="4"
                            >
                                <NText
                                    tag="h2"
                                    class="dashboard-card-title"
                                >
                                    Record name search
                                </NText>
                                <NFlex
                                    align="start"
                                    size="small"
                                >
                                    <NText
                                        class="small-text name-search-description"
                                        depth="3"
                                    >
                                        Searches globally across all zones for record name availability. Search accepts a hostname or full
                                        FQDN and supports * and ? wildcards.
                                    </NText>
                                    <NPopover
                                        trigger="hover"
                                        placement="top"
                                    >
                                        <template #trigger>
                                            <NIcon
                                                size="18"
                                                :component="Help"
                                                :color="theme.textColor3"
                                                class="help-icon"
                                            />
                                        </template>

                                        <div class="search-help">
                                            <div>
                                                <NText strong>FQDN:</NText>
                                                If the query ends with an existing zone name, it is treated as a full FQDN and searched
                                                directly.
                                            </div>

                                            <div>
                                                <NText strong>Wildcard:</NText>
                                                Queries containing
                                                <NText
                                                    code
                                                    class="mono"
                                                >
                                                    *
                                                </NText>
                                                or
                                                <NText
                                                    code
                                                    class="mono"
                                                >
                                                    ?
                                                </NText>
                                                are treated as wildcard patterns and searched directly.

                                                <div class="wildcard-help">
                                                    <div>
                                                        <NText
                                                            code
                                                            class="mono"
                                                        >
                                                            *
                                                        </NText>
                                                        matches any number of characters.
                                                    </div>
                                                    <div>
                                                        <NText
                                                            code
                                                            class="mono"
                                                        >
                                                            ?
                                                        </NText>
                                                        matches exactly one character.
                                                    </div>
                                                </div>
                                            </div>

                                            <div>
                                                <NText strong>Hostname:</NText>
                                                Otherwise, the query is treated as a hostname and searched across all existing zones.
                                            </div>
                                        </div>
                                    </NPopover>
                                </NFlex>
                            </NFlex>
                        </NFlex>
                    </template>
                    <NameSearchTable />
                </NCard>
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

.data-list-row {
    width: 100%;
    display: grid;

    align-items: center;
}

.search-help {
    max-width: 360px;
    font-size: 14px;
    line-height: 1.5;
}

.search-help > div + div {
    margin-top: 8px;
}
.wildcard-help {
    margin-top: 4px;
    padding-left: 12px;
}

.wildcard-help > div + div {
    margin-top: 2px;
}

.help-icon {
    cursor: help;
}
.mono {
    font-family: "Fira Code", monospace !important;
    font-weight: 1000;
    margin: 0 var(--spacing-xs);
}
</style>
