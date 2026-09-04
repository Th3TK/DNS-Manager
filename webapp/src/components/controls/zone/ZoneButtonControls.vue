<script setup lang="ts">
import { Trash } from "@vicons/tabler";
import { NButton, NIcon } from "naive-ui";

const emit = defineEmits<{
    delete: [];
}>();
</script>

<template>
    <NFlex>
        <NButton
            type="error"
            strong
            @click="emit('delete')"
        >
            <template #icon>
                <NIcon
                    :component="Trash"
                    size="16"
                />
            </template>
            Delete Zone
        </NButton>
    </NFlex>
</template>

<style scoped></style>
