<script setup lang="ts">
import { type User, type DNSZone } from "../../../types/api.types.ts";
import { type DataTableRowKey } from "naive-ui";
import { computed, ref, useTemplateRef } from "vue";
import { useRouter } from "vue-router";
import useFetch from "../../../composables/useFetch.ts";
import { getColumns } from "./columns.ts";
import { getZones } from "../../../services/api.ts";
import ClientDataTable from "../../data-table/ClientDataTable.vue";
import { getFilterConfig } from "./filterConfig.ts";
import type { TableExpose } from "../../../types/table.types.ts";
import ZoneControls from "../../controls/ZoneControls.vue";

const { data: users } = useFetch<User[]>("/users");
const router = useRouter();

const table = useTemplateRef<TableExpose<DNSZone>>("table");
const selectedKeys = ref<DataTableRowKey[]>([]);

const refresh = () => table.value?.refresh();
const handleClick = (row: DNSZone) => router.push(`/zones/${row.name}`);

const columns = computed(() => getColumns(refresh));
const filterConfig = computed(() => getFilterConfig(users.value ?? []));
const selectedRows = computed(() => table.value?.selectedRows ?? []);
</script>

<template>
    <ClientDataTable
        ref="table"
        v-model:selected-keys="selectedKeys"
        :rowKeys="['name']"
        :get-data="getZones"
        :columns="columns"
        :onCellClick="handleClick"
        :filterConfig="filterConfig"
    >
        <template #title> Zone List </template>
        <template #title-filters> Filtered Zones </template>
        <template #description> Double click on a zone to view its full details and records. </template>
        <template #controls>
            <ZoneControls
                type="table"
                :zones="selectedRows"
                @delete-error="refresh"
                @delete-success="refresh"
                @create-success="refresh"
            />
        </template>
    </ClientDataTable>
</template>

<style lang="css" scoped></style>
