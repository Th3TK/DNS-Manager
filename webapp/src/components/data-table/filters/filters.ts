import _, { filter, valuesIn } from "lodash";
import type { DataTableColumn, DataTableColumns } from "naive-ui";
import type { FilterConfig } from "../../../types/table.types";

type NaiveTableColumn<T> = DataTableColumn<T> & { key: keyof T; title: string };

export const filterFunctions = {
    freetext: (value: string, pattern: string): boolean => {
        const regexPattern = pattern
            .split("*")
            .map((part) => _.escapeRegExp(part))
            .join(".*");

        return new RegExp(`^${regexPattern}$`).test(value);
    },
    options: (value: string | number | boolean, selected: string[]): boolean => {
        return _.includes(selected, String(value));
    },
};

export const formatFilterText = <T>(
    key: keyof T,
    value: string | string[],
    columns: DataTableColumns<T>,
    filterConfig: FilterConfig<T>,
) => {
    const column = _.find(
        columns,
        (col): col is NaiveTableColumn<T> => "key" in col && col.key === key && "title" in col && typeof col.title === "string",
    );

    if (!column || !filterConfig[key]) return `${String(key)}: ${value}`;

    if (filterConfig[key]?.type === "freetext") {
        return `${column.title} matching: ${value}`;
    }

    if (filterConfig[key]?.type === "options") {
        const dict: Record<string | number, string> = _.mapValues(_.keyBy(filterConfig[key]?.options, "value"), "label");
        const values = [value].flat();
        const labels = values.map((v) => dict[v]);

        return `${column.title}: ${labels.join(", ")}`;
    }
};
