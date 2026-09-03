<script setup lang="ts">
import { Copy as IconCopy } from "@vicons/tabler";
import { NButton, NIcon, NText } from "naive-ui";

const props = defineProps<{
    value: string;
    monospace?: boolean;
    copyOption?: boolean;
}>();

const copy = () => {
    navigator.clipboard.writeText(props.value);
};
</script>

<template>
    <NText
        :class="{
            container: true,
            monospace: monospace,
        }"
        @dblclick.stop
    >
        {{ value }}
        <NButton
            v-if="copyOption && value"
            quaternary
            circle
            size="tiny"
            class="copy-button"
            @click="copy"
        >
            <template #icon>
                <NIcon
                    :component="IconCopy"
                    size="16"
                />
            </template>
        </NButton>
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
