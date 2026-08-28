<script setup lang="ts">
import { type DNSZone, type ChangeHistoryEntry } from "../../types/api.types";
import { NFlex, NText, type DataTableRowKey } from "naive-ui";
import { computed, onMounted, ref } from "vue";
import BaseDataTable from "../../components/BaseDataTable/BaseDataTable.vue";
import { useRouter } from "vue-router";
import type { FilterConfig } from "../../types/table.types.ts";
import { columns } from "./columns.ts";
import { getAllChangeHistoryActors, getChangeHistory } from "../../services/api.ts";

const data = ref<ChangeHistoryEntry[]>([]);
const total = ref(0);
const loading = ref(false);
const selectedKeys = ref<DataTableRowKey[]>([]);

const router = useRouter();
const handleRowClick = (row: ChangeHistoryEntry) => router.push(`/history/${row.entry_uuid}`);

const actors = ref<string[]>([]);

const filterConfig = computed<FilterConfig<ChangeHistoryEntry>>(() => ({
    action: {
        type: "options",
        options: [
            { label: "Created", value: "created" },
            { label: "Changed", value: "Changed" },
            { label: "Deleted", value: "Deleted" },
            { label: "Restored", value: "Restored" },
            { label: "Permanently Deleted", value: "Permanently Deleted" },
        ],
    },

    actor: {
        type: "options",
        options: actors.value.map((e) => ({
            label: e,
            value: e,
        })),
    },

    affected_object_name: {
        type: "freetext",
    },
}));

onMounted(async () => {
    actors.value = await getAllChangeHistoryActors();
});
</script>

<template>
    <BaseDataTable
        v-model:selectedKeys="selectedKeys"
        v-model:data="data"
        v-model:total="total"
        v-model:loading="loading"
        :get-data="getChangeHistory"
        :columns="columns"
        :filterConfig="filterConfig"
        rowKey="entry_uuid"
        :row-props="
            (row: ChangeHistoryEntry) => ({
                onClick: () => handleRowClick(row),
            })
        "
        :row-class-name="() => 'clickable-row'"
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
                    Change History -
                    <NText depth="3"> {{ total }} Entries </NText>
                </NText>
                <NText depth="3">
                    Full action log of changes made to DNS objects through the application. Click a row to view details.
                </NText>
            </NFlex>
        </template>
    </BaseDataTable>
</template>

<style lang="css" scoped>
:deep(.clickable-row) {
    cursor: pointer !important;
}

:deep(.clickable-row td > *) {
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
