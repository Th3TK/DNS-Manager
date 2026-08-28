<script setup lang="ts" generic="T extends Record<string, any>">
import {
    NButton,
    NDataTable,
    NFlex,
    NIcon,
    NTag,
    type DataTableColumn,
    type DataTableColumns,
    type DataTableRowKey,
    type DataTableSortState,
} from "naive-ui";
import { computed, ref, watch } from "vue";
import { type DataPaginated, type FilterConfig, type Filters } from "../../types/table.types";
import AddFilterButton from "./filters/AddFilterButton.vue";
import _ from "lodash";
import { useErrorHandler } from "../../composables/useErrorHandler.ts";
import { isAxiosError } from "axios";
import { Refresh } from "@vicons/tabler";
import { useTableQuery } from "../../composables/useTableQuery.ts";

defineOptions({
    inheritAttrs: false,
});

const props = defineProps<{
    getData: (
        page: number,
        pageSize: number,
        filters: Filters<T>,
        sortBy: keyof T | null,
        sortOrder: "ascend" | "descend" | null,
    ) => Promise<DataPaginated<T>>;
    filterConfig: FilterConfig<T>;
    columns: DataTableColumns<T>;
    rowKey: keyof T;
}>();

const { handleError } = useErrorHandler();

const { filters, sorter, page, pageSize } = useTableQuery<T>();

const selectedKeys = defineModel<DataTableRowKey[]>("selectedKeys");
const data = defineModel<T[]>("data", { default: () => [] });
const total = defineModel<number>("total", { default: 0 });
const loading = defineModel<boolean>("loading", { default: false });

const getKey = computed(() => (row: T) => row[props.rowKey] as DataTableRowKey);
const filtersActive = computed(() => Object.entries(filters.value) as [keyof T, string | string[]][]);

// Without this, the table is correctly sorted but Naive UI renders the
// corresponding sort button as unsorted when the sorter is restored from the path queries.
const initializedColumns = computed(() =>
    props.columns.map((column) => {
        if (!("key" in column) || column.key == null) {
            return column;
        }

        return {
            ...column,
            sortOrder: sorter.value?.columnKey === column.key ? sorter.value.order : false,
        };
    }),
);

const removeFilter = (key: string) => {
    const { [key]: _, ...remaining } = filters.value;

    filters.value = remaining as Filters<T>;
};

const formatFilter = (key: string, value: string | string[]) => {
    const column = _.find(
        props.columns,
        (col): col is DataTableColumn<T> & { key: keyof T; title: string } =>
            "key" in col && col.key === key && "title" in col && typeof col.title === "string",
    );

    if (!column) return `${key}: ${value}`;

    if (_.isArray(value)) {
        return `${column.title}: ${value.join(", ")}`;
    }

    return `${column.title} containing: ${value}`;
};

const loadData = async () => {
    loading.value = true;

    try {
        const result = await props.getData(
            page.value,
            pageSize.value,
            filters.value,
            (sorter.value?.columnKey as keyof T | undefined) ?? null,
            sorter.value?.order || null,
        );

        data.value = result.items;
        total.value = result.total;
    } catch (error) {
        if (isAxiosError(error)) handleError(error);
        else throw error;
    } finally {
        loading.value = false;
    }
};

const handlePageChange = (newPage: number) => {
    page.value = newPage;
};

const handlePageSizeChange = (newPageSize: number) => {
    pageSize.value = newPageSize;
    page.value = 1;
};

const handleSorterChange = (newSorter: DataTableSortState | null) => {
    sorter.value = newSorter;
    page.value = 1;
};

watch(filters, () => {
    page.value = 1;
});

watch(
    [page, pageSize, filters, sorter],
    () => {
        void loadData();
    },
    {
        deep: true,
        immediate: true,
    },
);
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
                    {{ formatFilter(key as string, value) }}
                </NTag>
            </NFlex>
            <NFlex class="controls">
                <NButton
                    @click="loadData"
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
            :data="data"
            :loading="loading"
            :single-line="false"
            :single="false"
            :row-key="getKey"
            :pagination="{
                page: page,
                pageSize: pageSize,
                itemCount: total,
                showSizePicker: true,
                pageSizes: [5, 10, 25, 50, 100],
                onChange: handlePageChange,
                onUpdatePageSize: handlePageSizeChange,
            }"
            remote
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
