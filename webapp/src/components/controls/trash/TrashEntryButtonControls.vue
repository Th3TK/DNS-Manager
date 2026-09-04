<script setup lang="ts">
import { ArrowBackUp, TrashX } from "@vicons/tabler";
import { NButton, NFlex, NIcon } from "naive-ui";

const emit = defineEmits<{
    restore: [];
    delete: [];
}>();
</script>

<template>
    <NFlex>
        <NButton
            type="info"
            tertiary
            strong
            @click="emit('restore')"
        >
            <template #icon>
                <NIcon :component="ArrowBackUp" />
            </template>

            Restore
        </NButton>

        <NButton
            type="error"
            tertiary
            strong
            @click="emit('delete')"
        >
            <template #icon>
                <NIcon :component="TrashX" />
            </template>

            Delete permanently
        </NButton>
    </NFlex>
</template>
