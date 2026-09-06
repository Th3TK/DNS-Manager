<script setup lang="ts">
import { NFlex, NText, type DataTableRowKey } from "naive-ui";
import { computed, ref, useTemplateRef, watch } from "vue";
import { useRouter } from "vue-router";
import ClientDataTable from "../../data-table/ClientDataTable.vue";
import useFetch from "../../../composables/useFetch.ts";
import { getRecords } from "../../../services/api.ts";
import type { DNSRecord, User } from "../../../types/api.types";
import type { TableExpose } from "../../../types/table.types.ts";
import { getFilters } from "./filters.ts";
import { getColumns } from "./columns.ts";
import RecordControls from "../../controls/RecordControls.vue";

const props = defineProps<{
    zoneName: string;
}>();

const { data: users } = useFetch<User[]>("/users");
const router = useRouter();

const table = useTemplateRef<TableExpose<DNSRecord>>("table");
const loading = ref(false);
const selectedKeys = ref<DataTableRowKey[]>([]);

const columns = computed(() => getColumns(props.zoneName, refresh));
const filterConfig = computed(() => getFilters(users.value ?? []));

const refresh = () => table.value?.refresh();
const handleClick = (row: DNSRecord) => router.push(`/zones/${props.zoneName}/record/${row.name}/${row.type}`);

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
                        Zone Records
                        <NText depth="3"> ({{ table?.total ?? 0 }}) </NText>
                    </NText>
                    <NText
                        depth="3"
                        v-if="!selectedKeys.length"
                    >
                        Double click on a record to view its full details.
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
            <RecordControls
                :records="table?.selectedRows ?? []"
                :zoneName="zoneName"
                @delete-error="refresh"
                @delete-success="refresh"
                @edit-success="refresh"
                @create-success="refresh"
            />
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
