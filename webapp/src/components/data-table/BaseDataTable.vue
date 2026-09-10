<script setup lang="ts" generic="T extends Record<string, any>">
import {
    NButton,
    NDataTable,
    NFlex,
    NIcon,
    NTag,
    NText,
    type DataTableColumns,
    type DataTableRowKey,
    type PaginationInfo,
    type PaginationProps,
} from "naive-ui";
import { type FilterConfig, type TableRow } from "../../types/table.types.ts";
import AddFilterButton from "./filters/AddFilterButton.vue";
import { Refresh } from "@vicons/tabler";
import { useDataTable } from "../../composables/useDataTable.ts";
import { formatFilterText } from "../../utils/filters.ts";
import { computed, h, watch, type VNodeChild } from "vue";
import _ from "lodash";
import type { VNode } from "vue";

defineOptions({
    inheritAttrs: false,
});

const props = defineProps<{
    columns: DataTableColumns<T>;
    rowKeys: (keyof T)[];
    filterConfig?: FilterConfig<T>;
    hideHeader?: boolean;
    refresh?: () => void;
    onCellClick?: (row: T) => any;
    paginationPrefix?: (info: PaginationInfo) => VNodeChild;
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
} = useDataTable<T>(props.columns, props.filterConfig ?? {}, props.onCellClick);

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

const defaultPaginationPrefix = computed(
    () => (): VNode =>
        h(
            NText,
            {
                type: "primary",
                depth: 3,
                strong: true,
            },
            {
                default: () => (selectedKeys.value.length ? `Selected rows:  ${selectedKeys.value.length ?? 0}` : ""),
            },
        ),
);

const pagination = computed(
    () =>
        ({
            page: page.value,
            pageSize: pageSize.value,
            itemCount: total.value,
            showSizePicker: true,
            pageSizes: [10, 25, 50, 100],
            onUpdatePage: handlePageChange,
            onUpdatePageSize: handlePageSizeChange,
            prefix: props.paginationPrefix ?? defaultPaginationPrefix.value,
        }) as PaginationProps,
);

watch(filters, () => {
    selectedKeys.value = [];
});

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
        <NFlex
            v-if="!hideHeader"
            vertical
            :size="0"
            class="header"
        >
            <NText
                class="title"
                :type="filtersActive.length ? 'primary' : undefined"
            >
                <slot
                    v-if="filtersActive.length"
                    name="title-filters"
                />
                <slot
                    v-else
                    name="title"
                />
            </NText>
            <NText depth="3"> <slot name="description" /> </NText>
        </NFlex>
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
            :pagination="pagination"
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

.header {
    padding-bottom: var(--spacing-md);
}

.title {
    font-size: 32px;
    line-height: normal;
    margin-top: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
}
:deep(.n-pagination) {
    width: 100%;
}
:deep(.n-pagination-prefix) {
    flex: 1 !important;
    font-size: 16px;
}
</style>
