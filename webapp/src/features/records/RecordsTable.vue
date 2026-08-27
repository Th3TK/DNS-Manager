<script setup lang="ts">
import type { Record } from "../../types/api.types";
import { NButton, NFlex, NIcon, NText, type DataTableColumns, type DataTableRowKey } from "naive-ui";
import { computed, h, ref } from "vue";
import { textFilter } from "../../components/BaseDataTable/filters.ts";
import BaseDataTable from "../../components/BaseDataTable/BaseDataTable.vue";
import TextField from "../../components/BaseDataTable/fields/TextField.vue";
import { Plus as IconPlus, Trash as IconTrash } from "@vicons/tabler";
import BadgeField from "../../components/BaseDataTable/fields/BadgeField.vue";
import _ from "lodash";
import BooleanField from "../../components/BaseDataTable/fields/BooleanField.vue";

const props = defineProps<{
    data: Record[];
}>();

const searchValue = ref<string>("");
const selectedKeys = ref<DataTableRowKey[]>([]);

const authors = [...new Set(props.data.map((e) => e.author))];
const types = [...new Set(props.data.map((e) => e.type))];

const columns: DataTableColumns<Record> = [
    {
        type: "selection",
        multiple: true,
    },
    textFilter<Record>({
        title: "Name",
        key: "name",
        sorter: "default",
        render: (row: Record) =>
            h(TextField, {
                value: row.name,
                searchValue: searchValue.value,
                copyOption: true,
            }),
    }),

    {
        title: "Type",
        key: "type",
        sorter: "default",
        render: (row: Record) =>
            h(BadgeField, {
                value: row.type,
                variants: {
                    A: { type: "primary" },
                    AAAA: { type: "primary" },
                    CNAME: { type: "error" },
                    TXT: { type: "info" },
                    MX: { type: "success" },
                    SRV: { type: "success" },
                },
                default: {
                    bordered: false,
                    type: "default",
                },
            }),

        filterOptions: types.map((type) => ({ label: type, value: type })),
        filter: "default",
        filterMultiple: true,
        width: 150,
    },

    textFilter<Record>({
        title: "Content",
        key: "content",
        sorter: "default",
        render: (row: Record) =>
            h(TextField, {
                value: _.isArray(row.content) ? row.content.join() : row.content,
                searchValue: searchValue.value,
                copyOption: true,
            }),
    }),

    {
        title: "Origin",
        key: "origin",
        sorter: "default",
        render: (row: Record) =>
            h(BadgeField, {
                value: row.origin,
                variants: {
                    external: {
                        type: "default",
                    },
                    manual: {
                        type: "success",
                    },
                    "automatic => traefik": {
                        type: "info",
                    },
                },
                default: {
                    bordered: false,
                    round: true,
                },
            }),

        filterOptions: [
            { label: "External", value: "external" },
            { label: "Manual", value: "manual" },
            { label: "Automatic => Traefik", value: "automatic => traefik" },
        ],
        filter: "default",
        filterMultiple: true,
        width: 150,
    },
    {
        title: "TTL",
        key: "ttl",
        sorter: "default",
        width: 100,
    },
];

const count = computed(() => props.data.length);
</script>

<template>
    <BaseDataTable
        v-model:name="searchValue"
        v-model:selectedKeys="selectedKeys"
        :columns="columns"
        :data="props.data"
        :searchableFieldKeys="['name', 'content']"
        rowKey="name"
    >
        <template #header>
            <NFlex
                vertical
                :size="0"
                class="header"
            >
                <NText
                    tag="h2"
                    class="title"
                >
                    Records
                    <NText depth="3"> ({{ count }}) </NText>
                </NText>
                <NText depth="3"></NText>
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
    </BaseDataTable>
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
