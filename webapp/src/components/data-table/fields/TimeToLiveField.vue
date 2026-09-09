<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { NFlex, NIcon, NText, NTime, NTooltip } from "naive-ui";
import { Help, InfoCircle, QuestionMark } from "@vicons/tabler";

const TIME_30_DAYS = 2_592_000_000;

const props = defineProps<{
    deletionTimestamp: Date;
}>();

const now = ref(Date.now());

let timeout: ReturnType<typeof setTimeout> | undefined;

const expirationTimestamp = computed(() => props.deletionTimestamp.getTime() + TIME_30_DAYS);
const remainingSeconds = computed(() => Math.max(0, Math.floor((expirationTimestamp.value - now.value) / 1000)));

const display = computed(() => {
    const seconds = remainingSeconds.value;

    if (seconds < 60) {
        return "Less than a minute";
    }

    if (seconds < 3600) {
        const roundedMinutes = Math.floor(seconds / 60);
        return `${roundedMinutes} minute${roundedMinutes !== 1 ? "s" : ""}`;
    }

    if (seconds < 86400) {
        const roundedHours = Math.floor(seconds / 3600);
        return `${roundedHours} hour${roundedHours !== 1 ? "s" : ""}`;
    }

    const roundedDays = Math.floor(seconds / 86400);
    return `${roundedDays} day${roundedDays !== 1 ? "s" : ""}`;
});

const scheduleUpdate = () => {
    if (timeout) {
        clearTimeout(timeout);
    }

    const seconds = remainingSeconds.value;

    let delay: number;

    if (seconds < 60) {
        // We don't display seconds, so there is no need to update anymore.
        delay = Infinity;
    } else if (seconds < 60 * 60) {
        // Update when the minute changes.
        delay = (seconds % 60) * 1000 + 100;
    } else if (seconds < 24 * 60 * 60) {
        // Update when the hour changes.
        delay = (seconds % (60 * 60)) * 1000 + 100;
    } else {
        // Update when the day changes.
        delay = (seconds % (24 * 60 * 60)) * 1000 + 100;
    }

    if (Number.isFinite(delay)) {
        timeout = setTimeout(() => {
            now.value = Date.now();
            scheduleUpdate();
        }, delay);
    }
};

onMounted(() => scheduleUpdate());

onBeforeUnmount(() => {
    if (timeout) {
        clearTimeout(timeout);
    }
});
</script>

<template>
    <NFlex
        :size="6"
        align="center"
        @click.stop
    >
        <NTooltip trigger="hover">
            <template #trigger>
                <NText> {{ display }}</NText>
            </template>
            <NText class="tooltip">
                <NTime
                    :time="expirationTimestamp"
                    format="'Deletion scheduled for' MMMM do, yyyy 'at' HH:mm"
                />
            </NText>
        </NTooltip>
    </NFlex>
</template>

<style lang="css" scoped>
.tooltip {
    font-size: 14px;
}
</style>
