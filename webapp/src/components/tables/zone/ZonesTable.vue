<script setup lang="ts">
import { type User, type DNSZone } from "../../../types/api.types.ts";
import { type DataTableRowKey, NFlex, NText } from "naive-ui";
import { computed, ref, useTemplateRef, watch } from "vue";
import { useRouter } from "vue-router";
import useFetch from "../../../composables/useFetch.ts";
import { getColumns } from "./columns.ts";
import { getZones } from "../../../services/api.ts";
import ClientDataTable from "../../data-table/ClientDataTable.vue";
import { getFilterConfig } from "./filters.ts";
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
                    Zone List
                    <NText depth="3"> ({{ table?.total ?? 0 }}) </NText>
                </NText>
                <NText depth="3"> Double click on a zone to view its full details and records. </NText>
            </NFlex>
        </template>
        <template #controls>
            <ZoneControls
                :zones="selectedRows"
                @delete-error="refresh"
                @delete-success="refresh"
                @create-success="refresh"
            />
        </template>
    </ClientDataTable>
</template>

<style lang="css" scoped>
.header {
    padding-bottom: var(--spacing-md);
}

.title {
    line-height: normal;
    margin-top: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
}
</style>
