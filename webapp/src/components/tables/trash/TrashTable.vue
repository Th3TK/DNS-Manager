<script setup lang="ts">
import { NButton, NFlex, NIcon, NText, type DataTableRowKey } from "naive-ui";
import { computed, ref, useTemplateRef } from "vue";
import { useRouter } from "vue-router";
import type { TrashEntry, User } from "../../../types/api.types";
import type { FilterConfig, TableExpose } from "../../../types/table.types.ts";
import { getColumns } from "./columns.ts";
import { deleteTrashEntry, getTrash } from "../../../services/api.ts";
import RemoteDataTable from "../../data-table/RemoteDataTable.vue";
import useFetch from "../../../composables/useFetch.ts";
import _ from "lodash";
import ConfirmationModal from "../../modals/ConfirmationModal.vue";
import { getFilters } from "./filters.ts";
import { Trash as IconTrash } from "@vicons/tabler";
import { useErrorHandler } from "../../../composables/useErrorHandler.ts";
import { HttpStatusCode } from "axios";

const { data: users } = useFetch<User[]>("/users");
const { handleError } = useErrorHandler();

const table = useTemplateRef<TableExpose<TrashEntry>>("table");
const router = useRouter();
const handleClick = (row: TrashEntry) => router.push(`/trash/${row.entry_uuid}`);

const selectedKeys = ref<DataTableRowKey[]>([]);
const openedDeleteModal = ref(false);

const columns = computed(() => getColumns(() => table.value?.refresh()));
const filterConfig = computed(() => getFilters(users.value ?? []));

const onDelete = () => {
    if (_.isEmpty(selectedKeys.value)) return;

    Promise.all(selectedKeys.value.map((k) => deleteTrashEntry(k as string)))
        .then(() => (selectedKeys.value = []))
        .catch((error) => {
            if (error.response?.status === HttpStatusCode.NotFound) return;
            handleError(error);
        })
        .finally(() => table.value?.refresh?.());
};
</script>

<template>
    <RemoteDataTable
        ref="table"
        :rowKeys="['entry_uuid']"
        :get-data="getTrash"
        :columns="columns"
        :filterConfig="filterConfig"
        :onCellClick="handleClick"
        v-model:selected-keys="selectedKeys"
    >
        <template #controls>
            <NButton
                type="error"
                strong
                v-if="selectedKeys.length"
                @click="openedDeleteModal = true"
            >
                <template #icon>
                    <NIcon
                        :component="IconTrash"
                        size="16"
                    />
                </template>
                Delete Selected
            </NButton>
            <ConfirmationModal
                type="error"
                v-model:show="openedDeleteModal"
                @submit="onDelete"
            >
                <template #title> Permanent deletion </template>
                <template #description>
                    Selected items ({{ selectedKeys.length }}) will be permanently deleted. This action cannot be undone.
                </template>
            </ConfirmationModal>
        </template>
        <template #header>
            <NFlex
                vertical
                :size="0"
                class="header"
            >
                <NText
                    tag="h1"
                    class="title"
                >
                    Trash -
                    <NText depth="3"> {{ table?.total ?? 0 }} Entries </NText>
                </NText>
                <NText depth="3">
                    Contains deleted DNS zones and records. Items are permanently deleted after 30 days. Double click on a table row to view
                    item's full details.</NText
                >
            </NFlex>
        </template>
    </RemoteDataTable>
</template>

<style lang="css" scoped>
:deep(.clickable-row) {
    cursor: pointer !important;
}

:deep(.clickable-row td > *) {
    cursor: initial !important;
}

.header {
    padding-bottom: var(--spacing-md);
}

.title {
    line-height: normal;
    margin-top: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
}
</style>
