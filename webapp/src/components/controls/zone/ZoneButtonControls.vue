<script setup lang="ts">
import { Trash } from "@vicons/tabler";
import { NButton, NFlex, NIcon } from "naive-ui";
import { useAuthenticationStore } from "../../../stores/useAuthenticationStore";

const emit = defineEmits<{
    delete: [];
}>();

const authentication = useAuthenticationStore();
</script>

<template>
    <NFlex>
        <NButton
            type="error"
            strong
            @click="emit('delete')"
            :disabled="!authentication.isAdmin"
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
