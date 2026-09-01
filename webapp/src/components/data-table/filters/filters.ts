import _ from "lodash";
import type { DataTableColumn, DataTableColumns } from "naive-ui";

type NaiveTableColumn<T> = DataTableColumn<T> & { key: keyof T; title: string };

export const filterFunctions = {
    freetext: (value: string, pattern: string): boolean => {
        const regexPattern = pattern
            .split("*")
            .map((part) => _.escapeRegExp(part))
            .join(".*");

        return new RegExp(`^${regexPattern}$`).test(value);
    },
    options: (value: string, selected: string[]): boolean => _.includes(selected, value),
};

export const formatFilterText = <T>(key: string, value: string | string[], columns: DataTableColumns<T>) => {
    const column = _.find(
        columns,
        (col): col is NaiveTableColumn<T> => "key" in col && col.key === key && "title" in col && typeof col.title === "string",
    );

    if (!column) return `${key}: ${value}`;

    if (_.isArray(value)) return `${column.title}: ${value.join(", ")}`;

    return `${column.title} containing: ${value}`;
};
