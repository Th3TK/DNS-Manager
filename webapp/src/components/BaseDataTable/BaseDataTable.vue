<script setup lang="ts" generic="T extends Record<string, any>">
import { NDataTable, NFlex, NIcon, NInput, type DataTableColumns, type DataTableRowKey } from "naive-ui";
import { Search as IconSearch } from "@vicons/tabler";
import { computed } from "vue";

defineOptions({
    inheritAttrs: false,
});

const props = defineProps<{
    data: T[];
    columns: DataTableColumns<T>;
    rowKey: keyof T;
    searchableFieldKeys: (keyof T)[];
}>();

const searchValue = defineModel<string>("name", { default: "" });

const selectedKeys = defineModel<DataTableRowKey[]>("selectedKeys");

// prettier-ignore
const filteredData = computed(() =>
    props.data.filter((row) =>
        props.searchableFieldKeys.some((key) =>
            String(row[key]).toLowerCase().includes(searchValue.value.toLowerCase()),
        ),
    ),
);

const key = computed(() => (row: T) => row[props.rowKey] as DataTableRowKey);
</script>

<template>
    <NFlex
        class="container"
        vertical
    >
        <slot name="header" />
        <NFlex :vertical="false">
            <NInput
                v-model:value="searchValue"
                type="text"
                placeholder="Search"
                class="search"
            >
                <template #prefix>
                    <NIcon :component="IconSearch" />
                </template>
            </NInput>
            <slot name="controls" />
        </NFlex>

        <NDataTable
            v-bind="$attrs"
            :columns="props.columns"
            :data="filteredData"
            :single-line="false"
            :single="false"
            :row-key="key"
            v-model:checked-row-keys="selectedKeys"
            striped
            flex-height
            class="data-table"
        />
        <slot name="footer" />
    </NFlex>
</template>

<style lang="css" scoped>
.container {
    height: 100%;
    gap: var(--spacing-md);
}

.search {
    flex: 1;
}

.data-table {
    flex: 1;
}
</style>
