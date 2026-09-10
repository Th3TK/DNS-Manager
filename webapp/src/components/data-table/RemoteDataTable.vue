<script setup lang="ts" generic="T extends Record<string, any>">
import { NText, type DataTableColumns, type DataTableRowKey } from "naive-ui";
import { computed, ref, shallowRef, useTemplateRef, watch } from "vue";
import { type BaseDataTableExpose, type DataPaginated, type FilterConfig, type Filters } from "../../types/table.types.ts";
import { useErrorHandler } from "../../composables/useErrorHandler.ts";
import { isAxiosError } from "axios";
import BaseDataTable from "./BaseDataTable.vue";

const props = defineProps<{
    getData: (
        page: number,
        pageSize: number,
        filters: Filters<T>,
        filterConfig: FilterConfig<T>,
        sortBy: keyof T | null,
        sortOrder: "ascend" | "descend" | null,
    ) => Promise<DataPaginated<T>>;
    filterConfig: FilterConfig<T>;
    columns: DataTableColumns<T>;
    rowKeys: (keyof T)[];
    onCellClick?: (row: T) => void;
}>();

const { handleError } = useErrorHandler();

const table = useTemplateRef<BaseDataTableExpose<T>>("table");

const data = shallowRef<T[]>([]);
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
            props.filterConfig,
            (table.value.sorter?.columnKey as keyof T | undefined) ?? null,
            table.value.sorter?.order || null,
        );

        data.value = result.items;
        total.value = result.total;
        selectedKeys.value = [];
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

const selectedRows = computed(() => table.value?.selectedRows ?? []);

defineExpose({
    total: total,
    refresh: loadData,
    selectedRows: selectedRows,
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
        :onCellClick="onCellClick"
        ref="table"
        remote
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
