<script setup lang="ts">
import { NFlex, NText } from "naive-ui";
import { computed, useTemplateRef } from "vue";
import { useRouter } from "vue-router";
import useFetch from "../../../composables/useFetch.ts";
import { getChangeHistory } from "../../../services/api.ts";
import type { ChangeHistoryEntry, User } from "../../../types/api.types";
import type { TableExpose } from "../../../types/table.types.ts";
import RemoteDataTable from "../../data-table/RemoteDataTable.vue";
import { columns } from "./columns.ts";
import { getFilters } from "./filters.ts";

const { data: users } = useFetch<User[]>("/users");

const table = useTemplateRef<TableExpose<ChangeHistoryEntry>>("table");
const router = useRouter();
const handleClick = (row: ChangeHistoryEntry) => router.push(`/history/${row.entry_uuid}`);

const filterConfig = computed(() => getFilters(users.value ?? []));
</script>

<template>
    <RemoteDataTable
        ref="table"
        :rowKeys="['entry_uuid']"
        :get-data="getChangeHistory"
        :columns="columns"
        :filterConfig="filterConfig"
        :onCellClick="handleClick"
    >
        <template #header> Change History Logs </template>
        <template #header-filters> Filtered Logs </template>
        <template #description>
            Full action log of changes made to DNS objects through the application. Double click on a row to view action details.
        </template>
    </RemoteDataTable>
</template>

<style lang="css" scoped></style>
