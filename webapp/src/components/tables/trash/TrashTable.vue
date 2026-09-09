<script setup lang="ts">
import { type DataTableRowKey } from "naive-ui";
import { computed, ref, useTemplateRef } from "vue";
import { useRouter } from "vue-router";
import type { TrashEntry, User } from "../../../types/api.types";
import type { TableExpose } from "../../../types/table.types.ts";
import { getColumns } from "./columns.ts";
import { getTrash } from "../../../services/api.ts";
import RemoteDataTable from "../../data-table/RemoteDataTable.vue";
import useFetch from "../../../composables/useFetch.ts";
import { getFilters } from "./filters.ts";
import TrashControls from "../../controls/TrashControls.vue";

const { data: users } = useFetch<User[]>("/users");

const table = useTemplateRef<TableExpose<TrashEntry>>("table");
const router = useRouter();

const selectedKeys = ref<DataTableRowKey[]>([]);

const columns = computed(() => getColumns(() => table.value?.refresh()));
const filterConfig = computed(() => getFilters(users.value ?? []));

const handleClick = (row: TrashEntry) => router.push(`/trash/${row.entry_uuid}`);
const refresh = () => table.value?.refresh();
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
        <template #title> Trash Items </template>
        <template #title-filters> Filtered Trash Items </template>
        <template #description>
            Contains deleted DNS zones and records. Items are permanently deleted after 30 days. Double click on a table row to view item's
            full details.
        </template>
        <template #controls>
            <TrashControls
                type="table"
                :entries="table?.selectedRows ?? []"
                @delete-error="refresh"
                @delete-success="refresh"
                @restore-error="refresh"
                @restore-success="refresh"
            />
        </template>
    </RemoteDataTable>
</template>

<style lang="css" scoped></style>
