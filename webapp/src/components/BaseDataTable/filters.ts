import { h, reactive } from "vue";
import type { DataTableBaseColumn } from "naive-ui";
import TextFilterMenu from "./menus/TextFilterMenu.vue";

export const textFilter = <T>(column: DataTableBaseColumn<T>): DataTableBaseColumn<T> => {
    const filteredColumn = reactive({
        ...column,
        filterOptionValue: null as string | null,
        filterOptions: [],

        renderFilterMenu: () =>
            h(TextFilterMenu, {
                modelValue: filteredColumn.filterOptionValue ?? "",
                "onUpdate:modelValue": (value: string) => {
                    filteredColumn.filterOptionValue = value || null;
                },
            }),

        filter: (value: any, row: T) => {
            if (!value) return true;

            return String(row[column.key as keyof T])
                .toLowerCase()
                .includes(String(value).toLowerCase());
        },
    });

    return filteredColumn;
};
