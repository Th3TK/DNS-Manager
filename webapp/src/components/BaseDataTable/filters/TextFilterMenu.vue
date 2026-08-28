<script setup lang="ts">
import { NFlex, NInput, NText } from "naive-ui";

const value = defineModel<string>({
    required: true,
});
</script>

<template>
    <NFlex
        vertical
        size="large"
        class="container"
    >
        <NFlex
            vertical
            size="small"
        >
            <NText class="label"> Free-text filter </NText>

            <NText
                depth="3"
                class="description"
            >
                Only rows containing this text will be shown.
            </NText>
        </NFlex>
        <NInput
            v-model:value="value"
            size="large"
            placeholder="Enter filter value"
        />
    </NFlex>
</template>

<style lang="css" scoped>
.container {
    padding: var(--spacing-md) var(--spacing-sm);
    gap: var(--spacing-lg);
    width: 280px;
}

.label {
    font-weight: 800;
    font-size: 14px;
    line-height: 1;
}

.description {
    font-size: 12px;
    line-height: 1;
}
</style>
