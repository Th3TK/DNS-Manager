<script setup lang="ts">
import { AxiosError } from "axios";

import type { DNSRecord } from "../../types/api.types.ts";

import { computed, toRef, watch } from "vue";
import { useRecordActions } from "../../composables/useRecordActions.ts";
import RecordDropdownControls from "./record/RecordDropdownControls.vue";
import _ from "lodash";
import RecordButtonControls from "./record/RecordButtonControls.vue";
import RecordTableControls from "./record/RecordTableControls.vue";
import CreateRecordModal from "../modals/CreateRecordModal.vue";
import ConfirmationModal from "../modals/ConfirmationModal.vue";
import { NText } from "naive-ui";

defineOptions({
    inheritAttrs: false,
});

const props = defineProps<{
    zoneName: string;
    records: DNSRecord | DNSRecord[];
    type: "dropdown" | "current" | "table";
    onDeleteError?: (error?: AxiosError) => void;
    onDeleteSuccess?: () => void;
    onCreateSuccess?: (record: DNSRecord) => void;
    onEditSuccess?: (record: DNSRecord) => void;
}>();

const records = toRef(props, "records");
const singularRecord = computed(() => [props.records].flat()?.[0] as DNSRecord | undefined);

const { deleteModalOpened, createModalOpened, editModalOpened, onDelete, onNavigate } = useRecordActions(
    props.onDeleteSuccess,
    props.onDeleteError,
);

const numberOfInternalRecords = computed(() => [records.value].flat().filter((r) => r.origin !== "external").length);
const numberOfExternalRecords = computed(() => [records.value].flat().filter((r) => r.origin === "external").length);

const recordsList = computed(() => [records.value].flat());
const record = computed(() => (_.isArray(records.value) ? null : records.value));
</script>
<template>
    <RecordDropdownControls
        v-if="type === 'dropdown' && record"
        v-bind="$attrs"
        :show-edit="record.origin !== 'external'"
        @navigate="() => onNavigate(record as DNSRecord)"
        @delete="deleteModalOpened = true"
        @edit="editModalOpened = true"
    />
    <RecordButtonControls
        v-else-if="type === 'current' && record"
        v-bind="$attrs"
        :show-edit="record.origin !== 'external'"
        @delete="deleteModalOpened = true"
        @edit="editModalOpened = true"
    />
    <RecordTableControls
        v-else-if="type === 'table'"
        v-bind="$attrs"
        @delete="deleteModalOpened = true"
        @create="createModalOpened = true"
        :show-delete="Boolean(recordsList.length)"
    />
    <ConfirmationModal
        type="error"
        v-model:show="deleteModalOpened"
        @submit="() => onDelete(recordsList)"
    >
        <template #title> Record{{ recordsList.length > 1 ? "s" : "" }} deletion </template>
        <template #description>
            <NText v-if="recordsList.length > 1">
                Selected records ({{ recordsList.length }}) will be
                <NText v-if="!numberOfInternalRecords">permanently deleted. This action cannot be undone.</NText>
                <NText v-else-if="!numberOfExternalRecords">moved to trash.</NText>
                <NText v-else>
                    deleted. Internal records ({{ numberOfInternalRecords }}) will be moved to trash, while external records ({{
                        numberOfExternalRecords
                    }}) will be permanently deleted.
                </NText>
            </NText>
            <NText v-else>
                Selected record will be
                <NText v-if="singularRecord?.origin === 'external'"> permanently deleted. This action cannot be undone.</NText>
                <NText v-else> moved to trash.</NText>
            </NText>
        </template>
    </ConfirmationModal>
    <CreateRecordModal
        @submit="onCreateSuccess"
        :zone-name="zoneName"
        v-model:show="createModalOpened"
    />
    <CreateRecordModal
        v-if="record"
        @submit="onEditSuccess"
        :zone-name="zoneName"
        :modifying="record"
        v-model:show="editModalOpened"
    />
</template>
