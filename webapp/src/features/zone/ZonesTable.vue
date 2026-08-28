<script setup lang="ts">
import { type User, type DNSZone } from "../../types/api.types";
import { NButton, NFlex, NIcon, NText, type DataTableRowKey } from "naive-ui";
import { computed, ref } from "vue";
import BaseDataTable from "../../components/BaseDataTable/BaseDataTable.vue";
import { Plus as IconPlus, Trash as IconTrash } from "@vicons/tabler";
import { useRouter } from "vue-router";
import type { FilterConfig, Filters } from "../../types/table.types.ts";
import useFetch from "../../composables/useFetch.ts";
import _ from "lodash";
import { columns } from "./columns.ts";
import { getZones } from "../../services/api.ts";

const data = ref<DNSZone[]>([]);
const total = ref(0);
const loading = ref(false);
const selectedKeys = ref<DataTableRowKey[]>([]);

const { data: users } = useFetch<User[]>("/users");

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
</script>

<template>
    <BaseDataTable
        v-model:selectedKeys="selectedKeys"
        v-model:data="data"
        v-model:total="total"
        v-model:loading="loading"
        :get-data="getZones"
        :columns="columns"
        :filterConfig="filterConfig"
        rowKey="name"
        :row-props="
            (row: DNSZone) => ({
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
                    DNSZone list
                    <NText depth="3"> ({{ total }}) </NText>
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
                Delete DNSZone
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
                Create DNSZone
            </NButton>
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
