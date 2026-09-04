<script setup lang="ts">
import { Edit, Trash } from "@vicons/tabler";
import { NButton, NFlex, NIcon } from "naive-ui";

const emit = defineEmits(["delete", "edit"]);

const props = defineProps<{
    showEdit: boolean;
}>();
</script>

<template>
    <NFlex>
        <NButton
            v-if="showEdit"
            type="warning"
            strong
            @click="emit('edit')"
        >
            <template #icon>
                <NIcon
                    :component="Edit"
                    size="16"
                />
            </template>
            Edit Record
        </NButton>
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
            Delete Record
        </NButton>
    </NFlex>
</template>

<style scoped></style>
