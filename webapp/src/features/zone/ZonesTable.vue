<script setup lang="ts">
import type { Zone } from "../../types/api.types";
import { NButton, NFlex, NIcon, NTag, NText, type DataTableColumns, type DataTableRowKey } from "naive-ui";
import { computed, h, ref } from "vue";
import { textFilter } from "../../components/BaseDataTable/filters.ts";
import BaseDataTable from "../../components/BaseDataTable/BaseDataTable.vue";
import TextField from "../../components/BaseDataTable/fields/TextField.vue";
import { Plus as IconPlus, Trash as IconTrash } from "@vicons/tabler";
import BadgeField from "../../components/BaseDataTable/fields/BadgeField.vue";
import UserField from "../../components/BaseDataTable/fields/UserField.vue";
import { useRouter } from "vue-router";

const props = defineProps<{
    data: Zone[];
}>();

const router = useRouter();

const searchValue = ref<string>("");
const selectedKeys = ref<DataTableRowKey[]>([]);

const authors = [...new Set(props.data.map((e) => e.author))];

const columns: DataTableColumns<Zone> = [
    {
        type: "selection",
        multiple: false,
    },
    textFilter<Zone>({
        title: "Name",
        key: "name",
        sorter: "default",
        render: (row: Zone) =>
            h(TextField, {
                value: row.name,
                searchValue: searchValue.value,
                copyOption: true,
            }),
    }),

    textFilter<Zone>({
        title: "Comment",
        key: "comment",
        sorter: "default",
        render: (row: Zone) =>
            h(TextField, {
                value: row.comment,
            }),
    }),
    {
        title: "Author",
        key: "author",
        sorter: "default",
        render: (row: Zone) =>
            h(TextField, {
                value: row.author,
            }),
        filterOptions: authors.map((author) => ({ label: author ?? "none", value: author })),
        filter: "default",
        filterMultiple: true,
    },
    {
        title: "Origin",
        key: "origin",
        sorter: "default",
        render: (row: Zone) =>
            h(BadgeField, {
                value: row.origin,
                variants: {
                    external: {
                        type: "default",
                        bordered: false,
                        round: true,
                    },
                    manual: {
                        type: "success",
                        bordered: false,
                        round: true,
                    },
                },
            }),

        filterOptions: [
            { label: "External", value: "external" },
            { label: "Manual", value: "manual" },
        ],
        filter: "default",
        filterMultiple: true,
    },
];

const handleRowClick = (row: Zone) => router.push(`/zones/${row.name}`);

const zoneCount = computed(() => props.data.length);

const internalZoneCount = computed(() => props.data.filter((zone) => zone.origin === "manual").length);

const externalZoneCount = computed(() => zoneCount.value - internalZoneCount.value);
</script>

<template>
    <BaseDataTable
        v-model:name="searchValue"
        v-model:selectedKeys="selectedKeys"
        :columns="columns"
        :data="props.data"
        :searchableFieldKeys="['name']"
        rowKey="name"
        :row-props="
            (row: Zone) => ({
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
                    Zone list
                    <NText depth="3"> ({{ zoneCount }}) </NText>
                </NText>
                <NText depth="3">{{ internalZoneCount }} internal, {{ externalZoneCount }} external</NText>
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
