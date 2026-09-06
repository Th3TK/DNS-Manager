<script setup lang="ts" generic="T extends Record<string, any>">
import { NButton, NDataTable, NFlex, NIcon, NTag, type DataTableColumns, type DataTableRowKey } from "naive-ui";
import { type FilterConfig, type TableRow } from "../../types/table.types.ts";
import AddFilterButton from "./filters/AddFilterButton.vue";
import { Refresh } from "@vicons/tabler";
import { useDataTable } from "../../composables/useDataTable.ts";
import { formatFilterText } from "./filters/filters.ts";
import { computed } from "vue";
import _ from "lodash";

defineOptions({
    inheritAttrs: false,
});

const props = defineProps<{
    columns: DataTableColumns<T>;
    rowKeys: (keyof T)[];
    filterConfig?: FilterConfig<T>;
    refresh?: () => void;
    onCellClick?: (row: T) => any;
}>();

const {
    filtersActive,
    removeFilter,
    initializedColumns,
    page,
    pageSize,
    handlePageChange,
    handlePageSizeChange,
    handleSorterChange,
    sorter,
    filters,
} = useDataTable<T>(props.columns, props.onCellClick);

const data = defineModel<T[]>("data", { default: () => [] });
const loading = defineModel<boolean>("loading", { default: false });
const total = defineModel<number>("total", { default: 0 });
const selectedKeys = defineModel<DataTableRowKey[]>("selectedKeys", { default: () => [] });

const keyedData = computed(() =>
    _.map(
        data.value,
        (e: T, i) =>
            ({
                ...e,
                key: [..._.map(props.rowKeys, (key) => e[key]), i].join(":::"),
            }) as TableRow<T>,
    ),
);

const selectedRows = computed(() => keyedData.value.filter((row) => selectedKeys.value.includes(row.key as DataTableRowKey)));

defineExpose({
    page,
    pageSize,
    filters,
    sorter,
    selectedRows,
});
</script>

<template>
    <NFlex
        class="container"
        vertical
    >
        <slot name="header" />
        <NFlex
            :vertical="false"
            class="full-controls"
        >
            <NFlex
                v-if="filterConfig"
                :size="8"
                class="filters"
            >
                <!-- @vue-expect-error -->
                <AddFilterButton
                    v-model="filters"
                    :columns="columns"
                    :filter-config="filterConfig"
                />
                <NTag
                    v-for="[key, value] in filtersActive"
                    :key="key"
                    type="primary"
                    closable
                    @close="removeFilter(key as string)"
                >
                    {{ formatFilterText(key as string, value, columns, filterConfig) }}
                </NTag>
            </NFlex>
            <NFlex class="controls">
                <NButton
                    v-if="refresh"
                    @click="refresh"
                    tertiary
                    type="default"
                >
                    <template #icon>
                        <NIcon :component="Refresh" />
                    </template>
                    Refresh
                </NButton>
                <slot name="controls" />
            </NFlex>
        </NFlex>

        <NDataTable
            v-bind="$attrs"
            v-model:checked-row-keys="selectedKeys"
            :columns="initializedColumns"
            :data="keyedData"
            :loading="loading"
            :row-key="(row) => row.key"
            :pagination="{
                page: page,
                pageSize: pageSize,
                itemCount: total,
                showSizePicker: true,
                pageSizes: [10, 25, 50, 100],
                onUpdatePage: handlePageChange,
                onUpdatePageSize: handlePageSizeChange,
            }"
            striped
            flex-height
            class="data-table"
            :sorter="sorter"
            @update:sorter="handleSorterChange"
        />
        <slot name="footer" />
    </NFlex>
</template>

<style lang="css" scoped>
.container {
    height: 100%;
    gap: var(--spacing-md);
}

.full-controls {
    align-items: end;
}

.filters {
    flex: 1;
    flex-wrap: wrap;
}

.data-table {
    flex: 1;
}

.controls {
    margin-left: auto;
}
</style>
