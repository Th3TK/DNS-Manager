<script setup lang="ts">
import { Trash, UserPlus } from "@vicons/tabler";
import { NButton, NFlex, NIcon } from "naive-ui";

const props = defineProps<{
    showDelete: boolean;
}>();

const emit = defineEmits(["create", "delete"]);
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
                    :component="UserPlus"
                    size="16"
                />
            </template>
            Create User
        </NButton>
    </NFlex>
</template>

<style scoped></style>
