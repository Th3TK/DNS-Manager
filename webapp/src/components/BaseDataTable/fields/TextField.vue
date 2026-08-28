<script setup lang="ts">
import { Copy as IconCopy } from "@vicons/tabler";
import { NButton, NFlex, NHighlight, NIcon, useThemeVars } from "naive-ui";

const themeVars = useThemeVars();

const props = defineProps<{
    value: string;
    searchValue?: string;
    copyOption?: boolean;
}>();

const copy = () => {
    navigator.clipboard.writeText(props.value);
};
</script>

<template>
    <NFlex
        class="container"
        @click.stop
    >
        <NHighlight
            :text="value"
            :patterns="searchValue ? [searchValue] : []"
            :highlight-style="{
                background: themeVars.primaryColor,
                fontWeight: 600,
                padding: '2px',
                borderRadius: '4px',
            }"
        />

        <NButton
            v-if="copyOption && value"
            quaternary
            circle
            size="tiny"
            @click="copy"
        >
            <template #icon>
                <NIcon
                    :component="IconCopy"
                    size="14"
                />
            </template>
        </NButton>
    </NFlex>
</template>

<style lang="css" scoped>
.container {
    display: flex;
    flex: 0;
    width: fit-content;
    gap: var(--spacing-xs) !important;
}
.search-highlight {
    background: color-mix(in srgb, var(--n-color-primary) 20%, transparent);
    color: var(--n-color-primary);
    border-radius: 3px;
    padding: 1px 3px;
}
</style>
