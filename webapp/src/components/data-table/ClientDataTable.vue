<script setup lang="ts" generic="T extends Record<string, any>">
import { type DataTableColumns, type DataTableRowKey } from "naive-ui";
import { computed, onMounted, ref, useTemplateRef } from "vue";
import type { TableExpose, BaseDataTableExpose, FilterConfig, TableRow } from "../../types/table.types.ts";
import { useErrorHandler } from "../../composables/useErrorHandler.ts";
import { filterFunctions } from "./filters/filters.ts";
import BaseDataTable from "./BaseDataTable.vue";
import _ from "lodash";
import { isAxiosError } from "axios";

const props = defineProps<{
    getData: () => Promise<T[]>;
    filterConfig: FilterConfig<T>;
    columns: DataTableColumns<T>;
    rowKeys: (keyof T)[];
    onCellClick?: (row: T) => any;
}>();

const { handleError } = useErrorHandler();

const table = useTemplateRef<BaseDataTableExpose<T>>("table");

const data = ref<TableRow<T>[]>([]);
const loading = defineModel<boolean>("loading", { default: false });
const total = computed(() => data.value.length);

const selectedKeys = defineModel<DataTableRowKey[]>("selectedKeys", { default: () => [] });
const selectedRows = computed(() => data.value.filter((row) => selectedKeys.value.includes(row.key as DataTableRowKey)));

const loadData = async () => {
    loading.value = true;

    try {
        const fetchedData = await props.getData();
        // ensuring rows have unique keys
        data.value = _.map(fetchedData, (e: T) => ({ ...e, key: _.map(props.rowKeys, (key) => e[key]).join(":::") }));
    } catch (error) {
        if (isAxiosError(error)) handleError(error);
        throw error;
    } finally {
        loading.value = false;
    }
};

//prettier-ignore
const filteredData = computed(() =>
    data.value.filter((item) =>
        _.entries(table.value!?.filters).every(([key, filterValue]) =>
            // @ts-expect-error
            filterFunctions[props.filterConfig[key]!.type](item[key], filterValue)
        ),
    ) as TableRow<T>[],
);

onMounted(loadData);

defineExpose({
    total: total,
    refresh: loadData,
    selectedRows: selectedRows,
});
</script>

<template>
    <BaseDataTable
        ref="table"
        v-model:selected-keys="selectedKeys"
        :data="filteredData"
        :loading="loading"
        :total="total"
        :refresh="loadData"
        :filter-config="filterConfig"
        :columns="columns"
        :row-keys="rowKeys"
        :onCellClick="onCellClick"
    >
        <template #header>
            <slot name="header" />
        </template>
        <template #controls>
            <slot name="controls" />
        </template>
        <template #footer>
            <slot name="footer" />
        </template>
    </BaseDataTable>
</template>
