<script setup lang="ts">
import { NBadge, NFlex, NPopover, NText, useThemeVars } from "naive-ui";
import _ from "lodash";
import { useRecordsStatusStore } from "../../../stores/useRecordsStatusStore";
import { storeToRefs } from "pinia";
import { computed } from "vue";

const props = defineProps<{
    zoneName: string;
}>();

const theme = useThemeVars();
const recordsStatus = useRecordsStatusStore();
const { data } = storeToRefs(recordsStatus);

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

const zoneCounts = computed(() => {
    const counts = {
        OK: 0,
        WARNING: 0,
        ERROR: 0,
        DISABLED: 0,
    };

    _.forEach(data.value?.statuses?.[props.zoneName], (types, name) => {
        _.forEach(types, (status) => {
            const displayStatus = recordsStatus.generateDisplayStatus(status);
            counts[displayStatus]++;
        });
    });

    return counts;
});
</script>

<template>
    <NFlex
        v-for="status in ['ERROR', 'WARNING', 'OK']"
        vertical
        :size="0"
        @click.stop
    >
        <NFlex
            align="center"
            size="small"
            class="status"
        >
            <NBadge
                dot
                :color="colors[status]"
            />
            <NText
                class="text"
                :type="types[status]"
                strong
            >
                {{ status === "OK" ? "OK" : _.capitalize(status) }}:
            </NText>
            <NText
                class="count"
                :type="types[status]"
                strong
            >
                {{ zoneCounts[status] }}
            </NText>
        </NFlex>
    </NFlex>
</template>
<style lang="css" scoped>
.status {
    cursor: default !important;
}
.text {
    width: 80px;
}
</style>
