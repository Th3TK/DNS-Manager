<script setup lang="ts">
import { NTag } from "naive-ui";
import { computed } from "vue";

const props = defineProps<{
    value: string;
    label?: string;
}>();

const types: Record<string, "primary" | "error" | "info" | "success" | "warning" | "default"> = {
    A: "primary",
    AAAA: "primary",
    CNAME: "error",
    TXT: "info",
    MX: "success",
    SRV: "success",
};

const type = computed(() => types[props.value] ?? "default");
</script>

<template>
    <NTag
        :type="type"
        :bordered="false"
    >
        {{ label ? label : value }}
    </NTag>
</template>

<style scoped></style>
