import type { DataTableColumns, DataTableRowKey, DataTableSortState } from "naive-ui";
import { computed, ref, watch } from "vue";
import type { Filters, TableRow } from "../types/table.types";
import { useTableQuery } from "./useTableQuery";

export function useDataTable<T extends Record<string, any>>(columns: DataTableColumns<T>) {
    const { filters, sorter, page, pageSize } = useTableQuery<T>();

    const filtersActive = computed(() => Object.entries(filters.value) as [keyof T, string | string[]][]);

    const removeFilter = (key: keyof T) => {
        const { [key]: _, ...remaining } = filters.value;
        filters.value = remaining as Filters<T>;
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

    // Without this, the table is correctly sorted but Naive UI renders the
    // corresponding sort button as unsorted when the sorter is restored from the path queries.
    const initializedColumns = computed(() =>
        columns.map((column) => {
            if (!("key" in column) || column.key == null) {
                return column;
            }

            return {
                ...column,
                sortOrder: sorter.value?.columnKey === column.key ? sorter.value.order : false,
            };
        }),
    );

    watch(filters, () => {
        page.value = 1;
    });

    return {
        filters,
        sorter,
        page,
        pageSize,
        filtersActive,
        removeFilter,
        handlePageChange,
        handlePageSizeChange,
        handleSorterChange,
        initializedColumns,
    };
}
