<script setup lang="ts">
import { Plus, Trash } from "@vicons/tabler";
import { NButton, NFlex, NIcon } from "naive-ui";

const props = defineProps<{
    showDelete: boolean;
}>();

const emit = defineEmits<{
    delete: [];
    create: [];
}>();
</script>

<template>
    <NFlex>
        <NButton
            type="error"
            strong
            v-if="showDelete"
            @click="emit('delete')"
        >
            <template #icon>
                <NIcon
                    :component="Trash"
                    size="16"
                />
            </template>
            Delete Selected
        </NButton>

        <NButton
            type="primary"
            strong
            @click="emit('create')"
        >
            <template #icon>
                <NIcon
                    :component="Plus"
                    size="16"
                />
            </template>
            Create Record
        </NButton>
    </NFlex>
</template>

<style scoped></style>
