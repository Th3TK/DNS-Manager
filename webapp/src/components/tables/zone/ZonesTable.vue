<script setup lang="ts">
import { type User, type DNSZone } from "../../../types/api.types.ts";
import { type DataTableRowKey } from "naive-ui";
import { computed, onUnmounted, ref, useTemplateRef, watch } from "vue";
import { useRouter } from "vue-router";
import useFetch from "../../../composables/useFetch.ts";
import { getColumns } from "./columns.ts";
import { getZones } from "../../../services/api.ts";
import ClientDataTable from "../../data-table/ClientDataTable.vue";
import { getFilterConfig } from "./filterConfig.ts";
import type { TableRow, TableExpose } from "../../../types/table.types.ts";
import ZoneControls from "../../controls/ZoneControls.vue";
import _ from "lodash";
import { isAxiosError } from "axios";
import { useErrorHandler } from "../../../composables/useErrorHandler.ts";

const { data: users } = useFetch<User[]>("/users");
const { handleError } = useErrorHandler();
const router = useRouter();

const data = ref<DNSZone[]>([]);
const recordCountLoaded = ref<boolean>(false);

const table = useTemplateRef<TableExpose<DNSZone>>("table");
const selectedKeys = ref<DataTableRowKey[]>([]);

const refresh = () => table.value?.refresh();
const handleClick = (row: DNSZone) => router.push(`/zones/${row.name}`);

const columns = computed(() => getColumns(refresh));
const filterConfig = computed(() => getFilterConfig(users.value ?? []));
const selectedRows = computed(() => table.value?.selectedRows ?? []);

const controller = new AbortController();

const getData = async () => {
    const zones = await getZones(true, controller.signal);

    // Start loading record counts, but don't await it.
    getZones(false, controller.signal)
        .then((zonesWithCounts) => {
            data.value = zonesWithCounts;
        })
        .catch((error) => {
            if (isAxiosError(error)) {
                handleError(error);
            }

            console.error(error);
        });

    return zones;
};

onUnmounted(() => {
    controller.abort();
});
</script>

<template>
    <ClientDataTable
        ref="table"
        v-model:selected-keys="selectedKeys"
        v-model:data="data"
        :rowKeys="['name']"
        :get-data="getData"
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
