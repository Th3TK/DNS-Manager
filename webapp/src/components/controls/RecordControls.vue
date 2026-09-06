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
    dropdown?: boolean;
    onDeleteError?: (error: AxiosError) => void;
    onDeleteSuccess?: () => void;
    onCreateSuccess?: (record: DNSRecord) => void;
    onEditSuccess?: (record: DNSRecord) => void;
}>();

const records = toRef(props, "records");

const { deleteModalOpened, createModalOpened, editModalOpened, onDelete, onNavigate } = useRecordActions(
    records,
    props.onDeleteSuccess,
    props.onDeleteError,
);

const numberOfInternalRecords = computed(() => [records.value].flat().filter((r) => r.origin !== "external").length);
const numberOfExternalRecords = computed(() => [records.value].flat().filter((r) => r.origin === "external").length);
</script>
<template>
    <RecordDropdownControls
        v-if="dropdown && !_.isArray(records)"
        v-bind="$attrs"
        @navigate="onNavigate"
        @delete="deleteModalOpened = true"
    />
    <RecordButtonControls
        v-else-if="!_.isArray(records)"
        v-bind="$attrs"
        @delete="deleteModalOpened = true"
        @edit="editModalOpened = true"
        :show-edit="records.origin !== 'external'"
    />
    <RecordTableControls
        v-else
        v-bind="$attrs"
        @delete="deleteModalOpened = true"
        @create="createModalOpened = true"
        :show-delete="Boolean(records.length)"
    />
    <ConfirmationModal
        type="error"
        v-model:show="deleteModalOpened"
        @submit="onDelete"
    >
        <template
            #title
            v-if="_.isArray(records) && records.length > 1"
        >
            Records deletion
        </template>
        <template
            #title
            v-else
        >
            Record deletion
        </template>
        <template #description>
            <NText v-if="_.isArray(records) && records.length > 1">
                Selected records ({{ records.length }}) will be
                <NText v-if="!numberOfInternalRecords">permanently deleted. This action cannot be undone.</NText>
                <NText v-else-if="!numberOfExternalRecords">moved to trash.</NText>
                <NText v-else>
                    deleted. Internal records ({{ numberOfInternalRecords }}) will be moved to trash, while external records ({{
                        numberOfExternalRecords
                    }}) will be permanently deleted.</NText
                >
            </NText>
            <NText v-else>
                Selected record will be
                <NText v-if="[records].flat()[0].origin === 'external'"> permanently deleted. This action cannot be undone.</NText>
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
        v-if="!_.isArray(records)"
        @submit="onEditSuccess"
        :zone-name="zoneName"
        :modifying="records"
        v-model:show="editModalOpened"
    />
</template>
