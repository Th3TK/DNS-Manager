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
                    <NText depth="3"> {{ table?.total ?? 0 }} Entries </NText>
                </NText>
                <NText depth="3">
                    Full action log of changes made to DNS objects through the application. Double click on a row to view action details.
                </NText>
            </NFlex>
        </template>
    </RemoteDataTable>
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
