<script setup lang="ts">
import { NBadge, NDescriptions, NDescriptionsItem, NFlex, NPopover, NText, NTime, useThemeVars } from "naive-ui";
import type { APIRecordStatus, DisplayedRecordStatus } from "../../../types/api.types";
import _ from "lodash";

const theme = useThemeVars();

const props = defineProps<{
    displayed_status: DisplayedRecordStatus;
    api_status: APIRecordStatus | null;
}>();

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
    <NPopover
        :disabled="!api_status"
        @click.stop
    >
        <template #trigger>
            <NFlex
                align="center"
                size="small"
                :class="{ 'status-active': api_status, status: true }"
            >
                <NBadge
                    dot
                    :color="colors[displayed_status]"
                />
                <NText
                    :type="types[displayed_status]"
                    :depth="displayed_status === 'DISABLED' ? 3 : 1"
                    strong
                >
                    {{ displayed_status === "OK" ? "OK" : _.capitalize(displayed_status) }}
                </NText>
            </NFlex>
        </template>
        <div
            v-if="api_status"
            class="grid"
        >
            <NText strong>Resolution check:</NText>
            <NText
                :type="api_status.resolution === 'NO_RESOLUTION' ? 'error' : api_status.resolution === 'MISMATCH' ? 'warning' : 'success'"
                strong
            >
                {{ api_status.resolution }}
            </NText>
            <NText strong>Reachability check:</NText>
            <NText
                :type="
                    api_status.reachability === 'UNREACHABLE' ? 'error' : api_status.reachability === 'REACHABLE' ? 'success' : undefined
                "
                :depth="!api_status.reachability || api_status.reachability === 'NOT_CHECKED' ? 3 : 1"
                strong
            >
                {{ api_status.reachability }}
            </NText>
        </div>
    </NPopover>
</template>
<style lang="css" scoped>
.status {
    cursor: default !important;
}
.status-active {
    cursor: help !important;
}
.grid {
    display: grid;
    grid-template-columns: 1fr auto;
    row-gap: 8px;
    column-gap: 24px;
    font-size: 14px;
}
</style>
