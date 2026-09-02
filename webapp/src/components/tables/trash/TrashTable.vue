<script setup lang="ts">
import { NFlex, NText } from "naive-ui";
import { computed, useTemplateRef } from "vue";
import { useRouter } from "vue-router";
import type { TrashEntry, User } from "../../../types/api.types";
import type { FilterConfig, TableExpose } from "../../../types/table.types.ts";
import { columns } from "./columns.ts";
import { getTrash } from "../../../services/api.ts";
import RemoteDataTable from "../../data-table/RemoteDataTable.vue";
import useFetch from "../../../composables/useFetch.ts";
import _ from "lodash";

const { data: users } = useFetch<User[]>("/users");

const table = useTemplateRef<TableExpose>("table");
const router = useRouter();
const handleRowClick = (row: TrashEntry) => router.push(`/trash/${row.entry_uuid}`);

const filterConfig = computed<FilterConfig<TrashEntry>>(() => ({
    actor: {
        type: "options",
        options: _.map(users.value, (user: User) => ({
            label: user.full_name || user.username,
            value: user.username,
        })),
    },
    object_type: {
        type: "options",
        options: [
            { label: "Zone", value: "zone" },
            { label: "Record", value: "record" },
        ],
    },
}));
</script>

<template>
    <RemoteDataTable
        ref="table"
        :rowKeys="['entry_uuid']"
        :get-data="getTrash"
        :columns="columns"
        :filterConfig="filterConfig"
        :row-props="
            (row: TrashEntry) => ({
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
                    Trash -
                    <NText depth="3"> {{ table?.total ?? 0 }} Entries </NText>
                </NText>
                <NText depth="3"> Contains deleted DNS zones and records. Entries are permanently deleted after 30 days. </NText>
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
