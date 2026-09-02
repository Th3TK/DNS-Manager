import type { DataTableColumns, DataTableRowKey, DataTableSortState } from "naive-ui";
import { computed, ref, watch } from "vue";
import type { Filters, TableRow } from "../types/table.types";
import { useTableQuery } from "./useTableQuery";
import _ from "lodash";
import type { TableBaseColumn, TableColumn } from "naive-ui/es/data-table/src/interface";

export function useDataTable<T extends Record<string, any>>(columns: DataTableColumns<T>, onCellClick?: (row: T) => void) {
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

    const isBaseColumn = <T>(column: TableColumn<T>): column is TableBaseColumn<T> => {
        return column.type === undefined && !("children" in column);
    };

    const initializedColumns = computed<TableColumn<T>[]>(() =>
        columns.map((column) => {
            if (!isBaseColumn(column)) {
                return column;
            }

            return {
                ...column,
                // without this, the table is correctly sorted but Naive UI renders the
                // corresponding sort button as unsorted when the sorter is restored from the path queries.
                sortOrder: sorter.value?.columnKey === column.key ? sorter.value.order : false,
                // on cell click
                cellProps: (row: T, rowIndex: number) => {
                    const props = column.cellProps?.(row, rowIndex);

                    return {
                        ...props,
                        ...(onCellClick && {
                            class: [props?.class, "clickable-cell"],
                            onClick: (event) => {
                                onCellClick(row);
                                props?.onClick?.(event);
                            },
                        }),
                    };
                },
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
