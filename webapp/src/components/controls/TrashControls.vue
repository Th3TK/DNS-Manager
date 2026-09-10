<script setup lang="ts">
import { AxiosError } from "axios";

import type { TrashEntry } from "../../types/api.types.ts";
import { useTrashActions } from "../../composables/useTrashActions.ts";

import TrashEntryDropdownControls from "./trash/TrashEntryDropdownControls.vue";
import TrashEntryButtonControls from "./trash/TrashEntryButtonControls.vue";
import ConfirmationModal from "../modals/ConfirmationModal.vue";
import _ from "lodash";
import TrashEntryTableControls from "./trash/TrashEntryTableControls.vue";
import { computed, toRef } from "vue";

defineOptions({
    inheritAttrs: false,
});

const props = defineProps<{
    entries: TrashEntry | TrashEntry[];
    type: "dropdown" | "current" | "table";
    onRestoreError?: (error: AxiosError) => void;
    onRestoreSuccess?: () => void;
    onDeleteError?: (error?: AxiosError) => void;
    onDeleteSuccess?: () => void;
}>();

const entries = toRef(props, "entries");

const { showCreateZoneConfirmation, showDeleteItemConfirmation, onRestore, onCreateZoneAndRestore, onDelete, onNavigate } = useTrashActions(
    props.onRestoreSuccess,
    props.onRestoreError,
    props.onDeleteSuccess,
    props.onDeleteError,
);

const entriesList = computed(() => [entries.value].flat());
const entry = computed(() => (_.isArray(entries.value) ? null : entries.value));
</script>

<template>
    <TrashEntryDropdownControls
        v-if="type === 'dropdown' && entry"
        v-bind="$attrs"
        @navigate="() => onNavigate(entry as TrashEntry)"
        @restore="() => onRestore(entry as TrashEntry)"
        @delete="showDeleteItemConfirmation = true"
    />

    <TrashEntryButtonControls
        v-else-if="type === 'current' && entry"
        v-bind="$attrs"
        @restore="() => onRestore(entry as TrashEntry)"
        @delete="showDeleteItemConfirmation = true"
    />

    <TrashEntryTableControls
        v-else-if="type === 'table'"
        :show-delete="!_.isEmpty(entriesList)"
        @delete="showDeleteItemConfirmation = true"
    />

    <ConfirmationModal
        v-model:show="showCreateZoneConfirmation"
        type="primary"
        @submit="() => entry && onCreateZoneAndRestore(entry)"
    >
        <template #title> Creating missing zone </template>

        <template #description>
            The zone for this record no longer exists. A new zone will be created automatically along with the restored record.
        </template>
    </ConfirmationModal>

    <ConfirmationModal
        v-model:show="showDeleteItemConfirmation"
        type="error"
        @submit="() => onDelete(entriesList)"
    >
        <template
            #title
            v-if="entry"
        >
            Permanent item deletion
        </template>
        <template
            #title
            v-else
        >
            Permanent deletion
        </template>
        <template
            #description
            v-if="entry"
        >
            This item will be permanently deleted. This action cannot be undone.
        </template>
        <template
            #description
            v-else
        >
            Selected items ({{ entriesList.length }}) will be permanently deleted. This action cannot be undone.
        </template>
    </ConfirmationModal>
</template>
