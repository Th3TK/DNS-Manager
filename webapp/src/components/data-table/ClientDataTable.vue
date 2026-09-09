<script setup lang="ts" generic="T extends Record<string, any>">
import { NText, type DataTableColumns, type DataTableRowKey } from "naive-ui";
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

const data = defineModel<T[]>("data", { default: () => [] });
const loading = defineModel<boolean>("loading", { default: false });
const selectedKeys = defineModel<DataTableRowKey[]>("selectedKeys", { default: () => [] });

const loadData = async () => {
    loading.value = true;

    try {
        data.value = await props.getData();
        selectedKeys.value = [];
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

const total = computed(() => filteredData.value.length);
const selectedRows = computed(() => table.value?.selectedRows ?? []);

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
        <template #title>
            <slot name="title" />
            <NText
                v-if="!loading"
                depth="3"
            >
                ({{ total }})
            </NText>
        </template>
        <template #title-filters>
            <slot name="title-filters" />
            <NText
                v-if="!loading"
                depth="3"
                type="primary"
            >
                ({{ total }})
            </NText>
        </template>
        <template #description>
            <slot name="description" />
        </template>
        <template #controls>
            <slot name="controls" />
        </template>
        <template #footer>
            <slot name="footer" />
        </template>
    </BaseDataTable>
</template>
