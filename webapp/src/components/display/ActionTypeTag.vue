<script setup lang="ts">
import { NTag } from "naive-ui";
import { computed } from "vue";
import type { ChangeHistoryAction } from "../../types/api.types";

const props = defineProps<{
    value: ChangeHistoryAction;
}>();

const types: Record<ChangeHistoryAction, "primary" | "error" | "info" | "success" | "warning" | "default"> = {
    created: "success",
    changed: "info",
    restored: "success",
    deleted: "warning",
    permanently_deleted: "error",
};

const type = computed(() => types[props.value] ?? "default");
</script>

<template>
    <NTag
        :type="type"
        :bordered="false"
        round
    >
        {{ value.replace("_", " ").toUpperCase() }}
    </NTag>
</template>

<style scoped></style>
