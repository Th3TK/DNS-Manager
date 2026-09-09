<script setup lang="ts">
import { NBadge, NButton, NCard, NFlex, NText, NTime, useThemeVars } from "naive-ui";
import DatetimeCountdown from "./DatetimeCountdown.vue";
import { useRouter } from "vue-router";
import { useRecordsStatusStore } from "../../stores/useRecordsStatusStore.ts";
import _ from "lodash";

const router = useRouter();
const theme = useThemeVars();

const recordsStatus = useRecordsStatusStore();

const types = {
    OK: "success",
    WARNING: "warning",
    ERROR: "error",
    DISABLED: "default",
};

const colors = {
    OK: theme.value.successColorPressed,
    WARNING: theme.value.warningColorPressed,
    ERROR: theme.value.errorColorPressed,
    DISABLED: theme.value.textColor3,
};
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
                        Records status
                    </NText>
                    <NText
                        class="small-text"
                        depth="3"
                    >
                        Shows the reachability status of DNS records. Click on a status to navigate to the filtered records page.
                    </NText>
                </NFlex>
            </NFlex>
        </template>
        <NFlex vertical>
            <NButton
                v-for="status in ['OK', 'WARNING', 'ERROR', 'DISABLED']"
                :key="status"
                quaternary
                block
                class="data-list-button"
                @click="
                    router.push({
                        path: '/records',
                        query: { displayed_status: status },
                    })
                "
            >
                <div class="data-list-row records-row">
                    <NFlex
                        class="data-list-cell"
                        align="center"
                    >
                        <NBadge
                            dot
                            :color="colors[status]"
                        />
                        <NText
                            :type="types[status]"
                            :depth="status === 'DISABLED' ? 3 : 1"
                            strong
                            class="medium-text"
                        >
                            {{ status === "OK" ? "OK" : _.capitalize(status) }}
                        </NText>
                    </NFlex>
                    <NText
                        strong
                        class="data-list-cell"
                        :type="types[status]"
                        :depth="status === 'DISABLED' ? 3 : 2"
                    >
                        {{ recordsStatus.data?.counts[status] }}
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
                    Last check:
                    <NTime
                        v-if="recordsStatus.data"
                        :time="recordsStatus.data.timestamp"
                        type="datetime"
                    />
                </NText>
                <DatetimeCountdown
                    v-if="recordsStatus.data"
                    class="small-text"
                    depth="3"
                    label="Next check in: "
                    :datetime="recordsStatus.data.next_check"
                />
            </NFlex>
        </template>
    </NCard>
</template>

<style scoped>
.data-list-row {
    width: 100%;
    display: grid;

    align-items: center;
    grid-template-columns: 180px 2fr;
}
.records-row > .data-list-cell:first-child {
    white-space: nowrap;
}
.data-list-cell {
    min-width: 0 !important;
}
.data-list-button {
    justify-content: flex-start;
    text-align: left;
    width: 100%;
}
.data-list-button :deep(.n-button__content) {
    width: 100%;
    justify-content: flex-start;
}
</style>
