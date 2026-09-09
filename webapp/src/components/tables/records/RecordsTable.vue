<script setup lang="ts">
import { NFlex, NText, type DataTableRowKey } from "naive-ui";
import { computed, ref, useTemplateRef, watch } from "vue";
import { useRouter } from "vue-router";
import ClientDataTable from "../../data-table/ClientDataTable.vue";
import useFetch from "../../../composables/useFetch.ts";
import { getAllRecords, getRecords } from "../../../services/api.ts";
import type { DNSRecord, DNSRecordExtended, User } from "../../../types/api.types";
import type { TableExpose } from "../../../types/table.types.ts";
import { getFilters } from "./filters.ts";
import { getColumns, getColumnsForAllRecordsTable } from "./columns.ts";
import RecordControls from "../../controls/RecordControls.vue";
import { useRecordsStatusStore } from "../../../stores/useRecordsStatusStore.ts";
import _ from "lodash";

const props = defineProps<
    | {
          global: true;
      }
    | {
          zoneName: string;
          global: boolean;
      }
>();

const router = useRouter();
const recordStatus = useRecordsStatusStore();

const { data: users } = useFetch<User[]>("/users");

const table = useTemplateRef<TableExpose<DNSRecordExtended>>("table");
const data = ref<DNSRecordExtended[]>([]);
const loading = ref(false);
const selectedKeys = ref<DataTableRowKey[]>([]);

const columns = computed(() => (props.global ? getColumnsForAllRecordsTable() : getColumns(props.zoneName, refresh)));
const filterConfig = computed(() => getFilters(users.value ?? []));

const refresh = () => table.value?.refresh();
const handleClick = (row: DNSRecordExtended) => router.push(`/zones/${row.zone_name}/record/${row.name}/${row.type}`);

const getRecordStatus = (record: DNSRecord) => recordStatus.data?.statuses?.[record.zone_name]?.[record.name]?.[record.type] ?? null;

const expandRecords = (records: DNSRecord[]) =>
    records.map((record) => {
        const status = getRecordStatus(record);

        return {
            ...record,
            api_status: status,
            displayed_status: recordStatus.generateDisplayStatus(status),
            status_timestamp: status?.timestamp ? new Date(status?.timestamp) : undefined,
        } as DNSRecordExtended;
    });

const getData = async () => {
    if (!props.global && !props.zoneName) {
        loading.value = true;
        return [];
    }

    const records = props.global ? await getAllRecords() : await getRecords(props.zoneName);
    return expandRecords(records);
};

watch(
    () => recordStatus.data,
    () => {
        if (_.isEmpty(data.value)) return;
        data.value = expandRecords(data.value);
    },
);
</script>

<template>
    <ClientDataTable
        ref="table"
        v-model:data="data"
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
                        :tag="global ? 'h1' : 'h2'"
                        class="title"
                    >
                        {{ global ? "Records List" : "Zone Records" }}
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
                v-if="!global"
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
