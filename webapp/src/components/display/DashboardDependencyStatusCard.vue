<script setup lang="ts">
import { Refresh } from "@vicons/tabler";
import { NBadge, NButton, NCard, NFlex, NIcon, NPopover, NText, NTime, NTooltip, useThemeVars } from "naive-ui";
import useFetch from "../../composables/useFetch";
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import _ from "lodash";

const { loading, error: dependencyErrors, refresh } = useFetch("/health");

const theme = useThemeVars();
const lastCheck = ref<Date>(new Date());

const getStatus = (code: "DNS_PROVIDER_UNAVAILABLE" | "DATABASE_UNAVAILABLE") =>
    _.isArray(dependencyErrors.value?.response?.data) && dependencyErrors.value?.response?.data.find((e) => e.code === code);

const dependencies = computed(() => [
    {
        name: "DNS Provider",
        error: getStatus("DNS_PROVIDER_UNAVAILABLE"),
    },
    {
        name: "PostgreSQL",
        error: getStatus("DATABASE_UNAVAILABLE"),
    },
]);

let refreshInterval: ReturnType<typeof setInterval>;

onMounted(() => {
    refreshInterval = setInterval(refresh, 60_000);
});

onUnmounted(() => {
    clearInterval(refreshInterval);
});
watch(loading, () => {
    lastCheck.value = new Date();
});
</script>

<template>
    <NCard>
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
                        Dependencies
                    </NText>
                    <NText
                        class="small-text"
                        depth="3"
                    >
                        Hover over errors for more details.
                    </NText>
                </NFlex>
                <NButton
                    class="refresh-button"
                    quaternary
                    @click="refresh"
                >
                    <NIcon
                        :component="Refresh"
                        :size="20"
                    />
                </NButton>
            </NFlex>
        </template>
        <NFlex vertical>
            <NTooltip
                v-for="dependency in dependencies"
                :key="dependency.name"
                :disabled="!dependency.error?.detail"
                :width="300"
                placement="right"
            >
                <template #trigger>
                    <div
                        class="data-list-row dependency"
                        :class="{ 'dependency-error': !!dependency.error }"
                        :style="{ '--hover-background': theme.buttonColor2Hover }"
                    >
                        <div class="data-list-cell">
                            <NText class="medium-text dependency-cell">
                                {{ dependency.name }}
                            </NText>
                        </div>

                        <div class="data-list-cell">
                            <NFlex
                                align="center"
                                :size="8"
                            >
                                <NBadge
                                    :color="
                                        loading
                                            ? theme.warningColorPressed
                                            : dependency.error
                                              ? theme.errorColorPressed
                                              : theme.successColorPressed
                                    "
                                    dot
                                />
                                <NText
                                    :type="loading ? 'warning' : dependency.error ? 'error' : 'success'"
                                    strong
                                >
                                    {{ loading ? "Loading" : dependency.error ? "Error" : "OK" }}
                                </NText>
                            </NFlex>
                        </div>
                    </div>
                </template>
                <NText class="tooltip-text">
                    {{ dependency.error.detail }}
                </NText>
            </NTooltip>
        </NFlex>
        <template #footer>
            <NFlex justify="space-between">
                <NText
                    class="small-text"
                    depth="3"
                >
                    Last check:
                    <NTime
                        :time="lastCheck"
                        type="datetime"
                    />
                </NText>
            </NFlex>
        </template>
    </NCard>
</template>

<style scoped>
.refresh-button {
    margin-left: auto;
    padding: 0;
    aspect-ratio: 1/1;
}

.data-list-row {
    width: 100%;
    display: grid;
    grid-template-columns: 200px 1fr;
    align-items: center;
}
.data-list-cell {
    min-width: 0 !important;
}

.dependency {
    padding: 4px var(--spacing-sm);
    border-radius: var(--spacing-xs);
    cursor: default;
}

.dependency-error {
    cursor: help;
}

.dependency:hover {
    background-color: var(--hover-background);
}

.tooltip-text {
    width: 200px;
    font-size: 14px;
}
</style>
