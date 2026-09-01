<script setup lang="ts" generic="T extends Record<string, any>">
import { type DataTableColumns, type DataTableRowKey } from "naive-ui";
import { ref, shallowRef, useTemplateRef, watch } from "vue";
import { type BaseDataTableExpose, type DataPaginated, type FilterConfig, type Filters, type TableRow } from "../../types/table.types.ts";
import { useErrorHandler } from "../../composables/useErrorHandler.ts";
import { isAxiosError } from "axios";
import BaseDataTable from "./BaseDataTable.vue";
import _ from "lodash";

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
    rowKeys: (keyof T)[];
}>();

const { handleError } = useErrorHandler();

const table = useTemplateRef<BaseDataTableExpose<T>>("table");

const data = shallowRef<TableRow<T>[]>([]);
const loading = ref<boolean>(false);
const total = ref<number>(0);
const selectedKeys = ref<DataTableRowKey[]>([]);

const loadData = async () => {
    loading.value = true;

    if (!table.value) return;

    try {
        const result = await props.getData(
            table.value.page,
            table.value.pageSize,
            table.value.filters,
            (table.value.sorter?.columnKey as keyof T | undefined) ?? null,
            table.value.sorter?.order || null,
        );

        data.value = _.map(result.items, (e: T) => ({ ...e, key: _.map(props.rowKeys, (key) => e[key]).join(":::") }));
        total.value = result.total;
    } catch (error) {
        if (isAxiosError(error)) handleError(error);
        else throw error;
    } finally {
        loading.value = false;
    }
};

watch(
    [() => table.value?.page, () => table.value?.pageSize, () => table.value?.filters, () => table.value?.sorter],
    () => {
        void loadData();
    },
    {
        deep: true,
        immediate: true,
    },
);

defineExpose({
    total,
});
</script>

<template>
    <BaseDataTable
        v-model:selected-keys="selectedKeys"
        :data="data"
        :loading="loading"
        :total="total"
        :refresh="loadData"
        :filter-config="filterConfig"
        :columns="columns"
        :row-keys="rowKeys"
        ref="table"
        remote
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
