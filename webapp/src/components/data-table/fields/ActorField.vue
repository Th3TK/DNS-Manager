<script setup lang="ts">
import { UserCircle as IconUserCircle, Eye as IconEye, Terminal2 as IconTerminal2 } from "@vicons/tabler";
import { NFlex, NIcon, NText } from "naive-ui";

const props = defineProps<{
    value?: string;
}>();
</script>

<template>
    <NFlex class="container">
        <NIcon
            v-if="value === 'system'"
            size="20"
            :component="IconTerminal2"
        />
        <NIcon
            v-else-if="value?.startsWith('watcher:')"
            size="20"
            :component="IconEye"
        />
        <NIcon
            v-else-if="value"
            size="20"
            :component="IconUserCircle"
        />

        <NText
            class="name"
            ellipsis
            @click.stop
        >
            {{ value ?? "-" }}
        </NText>
    </NFlex>
</template>

<style scoped>
.container {
    display: flex;
    align-items: center;
    width: fit-content;
    max-width: 100%;
    box-sizing: border-box;
    gap: 6px !important;
}

.name {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 1.2;
    text-overflow: ellipsis;
    width: fit-content;
    max-width: 100%;
}
</style>
