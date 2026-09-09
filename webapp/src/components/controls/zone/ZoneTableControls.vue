<script setup lang="ts">
import { Plus, Trash } from "@vicons/tabler";
import { NButton, NFlex, NIcon } from "naive-ui";
import { useAuthenticationStore } from "../../../stores/useAuthenticationStore";

const props = defineProps<{
    showDelete: boolean;
}>();

const emit = defineEmits<{
    delete: [];
    create: [];
}>();

const authentication = useAuthenticationStore();
</script>

<template>
    <NFlex>
        <NButton
            type="error"
            strong
            v-if="showDelete"
            @click="emit('delete')"
            :disabled="!authentication.isAdmin"
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
            :disabled="!authentication.isAdmin"
        >
            <template #icon>
                <NIcon
                    :component="Plus"
                    size="16"
                />
            </template>
            Create Zone
        </NButton>
    </NFlex>
</template>

<style scoped></style>
