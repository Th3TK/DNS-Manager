<script setup lang="ts">
import { AxiosError } from "axios";

import type { TrashEntry } from "../../types/api.types.ts";
import { useTrashActions } from "../../composables/useTrashActions.ts";

import TrashEntryDropdownControls from "./trash/TrashEntryDropdownControls.vue";
import TrashEntryButtonControls from "./trash/TrashEntryButtonControls.vue";
import ConfirmationModal from "../modals/ConfirmationModal.vue";

defineOptions({
    inheritAttrs: false,
});

const props = defineProps<{
    entry: TrashEntry;
    dropdown?: boolean;
    onRestoreError?: (error: AxiosError) => void;
    onRestoreSuccess?: () => void;
    onDeleteError?: (error: AxiosError) => void;
    onDeleteSuccess?: () => void;
}>();

const { showCreateZoneConfirmation, showDeleteItemConfirmation, onRestore, onCreateZoneAndRestore, onDelete, onNavigate } = useTrashActions(
    props.entry,
    props.onRestoreSuccess,
    props.onRestoreError,
    props.onDeleteSuccess,
    props.onDeleteError,
);
</script>

<template>
    <TrashEntryDropdownControls
        v-if="dropdown"
        v-bind="$attrs"
        @navigate="onNavigate"
        @restore="onRestore"
        @delete="showDeleteItemConfirmation = true"
    />

    <TrashEntryButtonControls
        v-else
        v-bind="$attrs"
        @restore="onRestore"
        @delete="showDeleteItemConfirmation = true"
    />

    <ConfirmationModal
        v-model:show="showCreateZoneConfirmation"
        type="primary"
        @submit="onCreateZoneAndRestore"
    >
        <template #title> Creating missing zone </template>

        <template #description>
            The zone for this record no longer exists. A new zone will be created automatically along with the restored record.
        </template>
    </ConfirmationModal>

    <ConfirmationModal
        v-model:show="showDeleteItemConfirmation"
        type="error"
        @submit="onDelete"
    >
        <template #title> Permanent item deletion </template>

        <template #description> This item will be permanently deleted. This action cannot be undone. </template>
    </ConfirmationModal>
</template>
