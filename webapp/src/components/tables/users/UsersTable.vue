<script setup lang="ts">
import { type User } from "../../../types/api.types.ts";
import { type DataTableRowKey } from "naive-ui";
import { computed, ref, useTemplateRef } from "vue";
import { getColumns } from "./columns.ts";
import { getUsers } from "../../../services/api.ts";
import ClientDataTable from "../../data-table/ClientDataTable.vue";
import type { TableExpose } from "../../../types/table.types.ts";
import { filters } from "./filters.ts";
import UserControls from "../../controls/UserControls.vue";

const table = useTemplateRef<TableExpose<User>>("table");
const selectedKeys = ref<DataTableRowKey[]>([]);

const refresh = () => table.value?.refresh();

const columns = computed(() => getColumns(refresh));
const selectedRows = computed(() => table.value?.selectedRows ?? []);
</script>

<template>
    <ClientDataTable
        ref="table"
        v-model:selected-keys="selectedKeys"
        :rowKeys="['username']"
        :get-data="getUsers"
        :columns="columns"
        :filterConfig="filters"
    >
        <template #title> Users List </template>
        <template #title-filters> Filtered Users </template>
        <template #description> Displays all accounts in the applicaton. </template>
        <template #controls>
            <UserControls
                type="table"
                :users="selectedRows"
                @create-success="refresh"
                @delete-error="refresh"
                @delete-success="refresh"
            />
        </template>
    </ClientDataTable>
</template>

<style lang="css" scoped></style>
