<script setup lang="ts">
import { ArrowBackUp, TrashX } from "@vicons/tabler";
import { NButton, NFlex, NIcon } from "naive-ui";
import { useAuthenticationStore } from "../../../stores/useAuthenticationStore";

const emit = defineEmits<{
    restore: [];
    delete: [];
}>();

const authentication = useAuthenticationStore();
</script>

<template>
    <NFlex>
        <NButton
            type="info"
            tertiary
            strong
            @click="emit('restore')"
            :disabled="!authentication.isAdmin"
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
            :disabled="!authentication.isAdmin"
        >
            <template #icon>
                <NIcon :component="TrashX" />
            </template>

            Delete permanently
        </NButton>
    </NFlex>
</template>
