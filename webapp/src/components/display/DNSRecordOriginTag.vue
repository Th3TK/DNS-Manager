<script setup lang="ts">
import { NTag } from "naive-ui";
import { computed } from "vue";
import type { DNSRecordOrigin } from "../../types/api.types";
import _ from "lodash";

const props = defineProps<{
    value: DNSRecordOrigin;
}>();

const origins: Record<DNSRecordOrigin, "primary" | "error" | "info" | "success" | "warning" | "default"> = {
    manual: "primary",
    "automatic => traefik": "info",
    external: "default",
};

const origin = computed(() => origins[props.value] ?? "default");
</script>

<template>
    <NTag
        :type="origin"
        :bordered="false"
    >
        {{ _.capitalize(value) }}
    </NTag>
</template>

<style scoped></style>
