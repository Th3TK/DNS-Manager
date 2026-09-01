<script setup lang="ts">
import { User as IconUser, Eye as IconEye, Terminal2 as IconTerminal2 } from "@vicons/tabler";
import { NIcon } from "naive-ui";

const props = defineProps<{
    value: string;
}>();
</script>

<template>
    <NFlex class="container">
        <NIcon
            v-if="value === 'system'"
            size="18"
            :component="IconTerminal2"
        />
        <NIcon
            v-else-if="value.startsWith('watcher:')"
            size="18"
            :component="IconEye"
        />
        <NIcon
            v-else
            size="18"
            :component="IconUser"
        />

        <NText
            class="name"
            ellipsis
        >
            {{ value }}
        </NText>
    </NFlex>
</template>

<style scoped>
.container {
    display: flex;
    align-items: center;
    min-width: 0;
    width: 100%;
    box-sizing: border-box;
    gap: 6px;
}

.name {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 1.2;
    text-overflow: ellipsis;
}
</style>
