<script setup lang="ts">
import { NText } from "naive-ui";

const props = defineProps<{
    value: string;
    monospace?: boolean;
}>();
</script>

<template>
    <NText
        :class="{
            container: true,
            monospace: monospace,
        }"
        @click.stop
    >
        {{ value }}
    </NText>
</template>

<style lang="css" scoped>
.search-highlight {
    background: color-mix(in srgb, var(--n-color-primary) 20%, transparent);
    color: var(--n-color-primary);
    border-radius: 3px;
    padding: 1px 3px;
}
.container {
    white-space: pre-line;
    cursor: initial;
}
.copy-button {
    margin-left: var(--spacing-xxs);
    transform: translateY(1px);
}
.monospace {
    font-family: monospace;
}
</style>
