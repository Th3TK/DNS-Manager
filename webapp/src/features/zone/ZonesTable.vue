<script setup lang="ts">
import { type User, type DNSZone } from "../../types/api.types";
import { type DataTableRowKey, NButton, NFlex, NIcon, NText, type DataTableColumn, type DataTableColumns } from "naive-ui";
import { computed, ref, useTemplateRef, watch } from "vue";
import { Plus as IconPlus, Trash as IconTrash } from "@vicons/tabler";
import { useRouter } from "vue-router";
import type { FilterConfig } from "../../types/table.types.ts";
import useFetch from "../../composables/useFetch.ts";
import _ from "lodash";
import { columns } from "./columns.ts";
import { getZones } from "../../services/api.ts";
import ClientDataTable from "../../components/data-table/ClientDataTable.vue";

const { data: users } = useFetch<User[]>("/users");

const table = useTemplateRef("table");
const selectedKeys = ref<DataTableRowKey[]>([]);

const router = useRouter();
const handleRowClick = (row: DNSZone) => router.push(`/zones/${row.name}`);

const filterConfig = computed<FilterConfig<DNSZone>>(() => ({
    name: {
        type: "freetext",
    },
    author: {
        type: "options",
        options: _.map(users.value, (user: User) => ({ label: user.full_name || user.username, value: user.username })),
    },
    comment: {
        type: "freetext",
    },
    origin: {
        type: "options",
        options: [
            { label: "External", value: "external" },
            { label: "Manual", value: "manual" },
        ],
    },
}));

const clickableColumns = computed<DataTableColumns<DNSZone>>(() =>
    columns.map(
        (col) =>
            ({
                ...col,
                cellProps: (row: DNSZone) =>
                    "key" in col && col.key
                        ? {
                              class: "clickable-cell",
                              onClick: () => handleRowClick(row),
                          }
                        : undefined,
            }) as DataTableColumn<DNSZone>,
    ),
);
</script>

<template>
    <ClientDataTable
        ref="table"
        v-model:selected-keys="selectedKeys"
        :rowKeys="['name']"
        :get-data="getZones"
        :columns="clickableColumns"
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
                    Zone list
                    <NText depth="3"> ({{ table?.total ?? 0 }}) </NText>
                </NText>
                <NText depth="3"> Click on a zone to view its full details and records. </NText>
            </NFlex>
        </template>
        <template #controls>
            <NButton
                type="error"
                strong
                v-if="selectedKeys.length"
            >
                <template #icon>
                    <NIcon
                        :component="IconTrash"
                        size="16"
                    />
                </template>
                Delete Zone
            </NButton>
            <NButton
                type="primary"
                strong
            >
                <template #icon>
                    <NIcon
                        :component="IconPlus"
                        size="16"
                    />
                </template>
                Create Zone
            </NButton>
        </template>
    </ClientDataTable>
</template>

<style lang="css" scoped>
:deep(.clickable-cell) {
    cursor: pointer !important;
}

:deep(.clickable-cell td > *) {
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
