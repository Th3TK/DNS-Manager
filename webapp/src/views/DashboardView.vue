<script setup lang="ts">
import {
    NBadge,
    NButton,
    NCard,
    NDivider,
    NFlex,
    NGrid,
    NGridItem,
    NIcon,
    NInput,
    NPopover,
    NText,
    NTooltip,
    useThemeVars,
} from "naive-ui";
import DashboardLayout from "../layouts/DashboardLayout.vue";
import { Help, Refresh, Search } from "@vicons/tabler";
import { useRouter } from "vue-router";
import DatetimeCountdown from "../components/display/DatetimeCountdown.vue";
import NameSearchTable from "../components/tables/name-search/NameSearchTable.vue";

const router = useRouter();
const theme = useThemeVars();

const TIME_5_MINUTES = 300000;

const dependencies = [
    {
        name: "DNS Provider",
        status: "ok",
        lastCheck: "2026-09-06 16:20:31",
    },
    {
        name: "PostgreSQL",
        status: "error",
        lastCheck: "2026-09-06 16:20:30",
    },
];

const records = {
    disabled: 219,
    ok: 102,
    error: 32,
    warning: 192,
};

const types = {
    ok: "success",
    disabled: "default",
    error: "error",
    warning: "warning",
};

const lastCheck = new Date(Date.now());
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
                <NCard class="content-card">
                    <template #header>
                        <NFlex class="header">
                            <NFlex
                                vertical
                                :size="4"
                            >
                                <NText
                                    tag="h2"
                                    class="title"
                                >
                                    Dependencies
                                </NText>
                                <NText
                                    class="small-text"
                                    depth="3"
                                >
                                    Shows the current status and last check time of each dependency. Hover over a dependency for more
                                    details.
                                </NText>
                            </NFlex>
                            <NButton
                                class="refresh-button"
                                quaternary
                            >
                                <NIcon
                                    :component="Refresh"
                                    :size="20"
                                />
                            </NButton>
                        </NFlex>
                    </template>
                    <NFlex vertical>
                        <div
                            v-for="dependency in dependencies"
                            :key="dependency.name"
                            class="data-list-row"
                            :cols="3"
                        >
                            <div class="data-list-cell">
                                <NText class="big-text dependency-cell">
                                    {{ dependency.name }}
                                </NText>
                            </div>

                            <div class="data-list-cell">
                                <NFlex
                                    align="center"
                                    :size="8"
                                >
                                    <NBadge
                                        :color="dependency.status === 'ok' ? theme.successColorPressed : theme.errorColorPressed"
                                        dot
                                    />
                                    <NText
                                        :type="dependency.status === 'ok' ? 'success' : 'error'"
                                        strong
                                    >
                                        {{ dependency.status === "ok" ? "OK" : "ERROR" }}
                                    </NText>
                                </NFlex>
                            </div>

                            <div class="data-list-cell">
                                <NText
                                    depth="3"
                                    class="small-text"
                                >
                                    {{ dependency.lastCheck }}
                                </NText>
                            </div>
                        </div>
                    </NFlex>
                </NCard>
            </NGridItem>

            <NGridItem>
                <NCard class="content-card">
                    <template #header>
                        <NFlex class="header">
                            <NFlex
                                vertical
                                :size="4"
                            >
                                <NText
                                    tag="h2"
                                    class="title"
                                >
                                    Records status
                                </NText>
                                <NText
                                    class="small-text"
                                    depth="3"
                                >
                                    Shows the reachability status of DNS records. Click on a status to navigate to the filtered records
                                    page.
                                </NText>
                            </NFlex>
                        </NFlex>
                    </template>
                    <NFlex vertical>
                        <NButton
                            v-for="status in ['ok', 'warning', 'error', 'disabled']"
                            :key="status"
                            quaternary
                            block
                            class="data-list-button"
                            @click="
                                router.push({
                                    path: '/records',
                                    query: { status },
                                })
                            "
                        >
                            <div class="data-list-row">
                                <NFlex
                                    class="data-list-cell"
                                    align="center"
                                >
                                    <NBadge
                                        dot
                                        :color="
                                            status === 'ok'
                                                ? theme.successColorPressed
                                                : status === 'warning'
                                                  ? theme.warningColorPressed
                                                  : status === 'error'
                                                    ? theme.errorColorPressed
                                                    : theme.textColor3
                                        "
                                    />
                                    <NText
                                        :type="types[status]"
                                        :depth="status === 'disabled' ? 3 : 1"
                                        strong
                                        class="big-text"
                                    >
                                        {{ status.toUpperCase() }}
                                    </NText>
                                </NFlex>
                                <NText
                                    strong
                                    class="data-list-cell"
                                    :type="types[status]"
                                    :depth="status === 'disabled' ? 3 : 2"
                                >
                                    {{ records[status] }}
                                </NText>
                            </div>
                        </NButton>
                    </NFlex>
                    <template #footer>
                        <NFlex justify="space-between">
                            <NText
                                class="small-text"
                                depth="3"
                            >
                                Last check: 2026-09-06 16:20:31
                            </NText>
                            <DatetimeCountdown
                                class="small-text"
                                depth="3"
                                label="Next check in: "
                                :datetime="new Date(lastCheck.getTime() + TIME_5_MINUTES)"
                            />
                        </NFlex>
                    </template>
                </NCard>
            </NGridItem>

            <NGridItem :span="2">
                <NCard class="content-card">
                    <template #header>
                        <NFlex class="header">
                            <NFlex
                                vertical
                                :size="4"
                            >
                                <NText
                                    tag="h2"
                                    class="title"
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
.title {
    margin: var(--spacing-xs) 0;
}

.header {
    align-items: center;
}

.refresh-button {
    margin-left: auto;
    padding: 0;
    aspect-ratio: 1/1;
}

.grid {
    height: 100%;
    box-sizing: border-box;
    grid-template-rows: auto 1fr;
}
.content-card {
    height: 100%;
    box-sizing: border-box;
}

.big-text {
    font-size: 18px;
}

.small-text {
    font-size: 14px;
}

.data-list-row {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    align-items: center;
}
.data-list-cell {
    min-width: 0 !important;
}
.data-list-button {
    justify-content: flex-start;
    text-align: left;
    width: 100%;
    padding-top: var(--spacing-md);
    padding-bottom: var(--spacing-md);
}
.data-list-button :deep(.n-button__content) {
    width: 100%;
    justify-content: flex-start;
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
