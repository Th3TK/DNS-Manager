<script setup lang="ts">
import { Plus as IconPlus, Trash as IconTrash } from "@vicons/tabler";
import _ from "lodash";
import { NButton, NFlex, NIcon, NText, type DataTableColumn, type DataTableColumns, type DataTableRowKey } from "naive-ui";
import { computed, ref, useTemplateRef } from "vue";
import { useRouter } from "vue-router";
import ClientDataTable from "../../data-table/ClientDataTable.vue";
import useFetch from "../../../composables/useFetch.ts";
import { getRecords } from "../../../services/api.ts";
import type { DNSRecord, User } from "../../../types/api.types";
import type { FilterConfig } from "../../../types/table.types.ts";
import { columns } from "./columns.ts";

const props = defineProps<{
    zoneName: string;
}>();

const { data: users } = useFetch<User[]>("/users");

const table = useTemplateRef("table");
const loading = ref(false);
const selectedKeys = ref<DataTableRowKey[]>([]);

const router = useRouter();
const handleClick = (row: DNSRecord) => router.push(`/zones/${props.zoneName}/record/${row.name}/${row.type}`);

const filterConfig = computed<FilterConfig<DNSRecord>>(() => ({
    zone_name: { type: "freetext" },
    name: { type: "freetext" },
    content: { type: "freetext" },
    comment: { type: "freetext" },
    type: {
        type: "options",
        options: [
            { label: "A", value: "A" },
            { label: "AAAA", value: "AAAA" },
            { label: "CNAME", value: "CNAME" },
            { label: "TXT", value: "TXT" },
            { label: "MX", value: "MX" },
            { label: "SRV", value: "SRV" },
            { label: "SOA", value: "SOA" },
            { label: "NS", value: "NS" },
        ],
    },
    author: {
        type: "options",
        options: _.map(users.value, (user: User) => ({ label: user.full_name || user.username, value: user.username })),
    },
}));

const getData = async () => {
    if (!props.zoneName) {
        loading.value = true;
        return [];
    }
    return await getRecords(props.zoneName);
};
</script>

<template>
    <ClientDataTable
        ref="table"
        v-model:loading="loading"
        v-model:selected-keys="selectedKeys"
        :rowKeys="['name', 'type']"
        :get-data="getData"
        :columns="columns"
        :onCellClick="handleClick"
        :filter-config="filterConfig"
    >
        <template #header>
            <NFlex>
                <NFlex
                    vertical
                    :size="0"
                    class="header"
                >
                    <NText
                        tag="h2"
                        class="title"
                    >
                        Zone records
                        <NText depth="3"> ({{ table?.total ?? 0 }}) </NText>
                    </NText>
                    <NText
                        depth="3"
                        v-if="!selectedKeys.length"
                    >
                        Click on a record to view its full details.
                    </NText>
                    <NText
                        v-else
                        type="primary"
                    >
                        Selected {{ selectedKeys.length }}
                    </NText>
                </NFlex>
                <slot name="header" />
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
                Delete Selected
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
                Create Record
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
