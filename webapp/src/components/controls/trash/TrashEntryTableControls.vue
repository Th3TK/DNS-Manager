<script setup lang="ts">
import { TrashX } from "@vicons/tabler";
import { NButton, NFlex, NIcon } from "naive-ui";
import { useAuthenticationStore } from "../../../stores/useAuthenticationStore";

const props = defineProps<{
    showDelete: boolean;
}>();

const emit = defineEmits(["delete"]);

const authentication = useAuthenticationStore();
</script>

<template>
    <NFlex v-if="showDelete">
        <NButton
            type="error"
            strong
            @click="emit('delete')"
            :disabled="!authentication.isAdmin"
        >
            <template #icon>
                <NIcon
                    :component="TrashX"
                    size="16"
                />
            </template>
            Delete Selected
        </NButton>
    </NFlex>
</template>

<style scoped></style>
