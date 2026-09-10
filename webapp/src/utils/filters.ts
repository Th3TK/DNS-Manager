import _, { filter, valuesIn } from "lodash";
import type { DataTableColumn, DataTableColumns } from "naive-ui";
import type { FilterConfig, Filters, FilterType, RangeValue } from "../types/table.types";
import type { LocationQuery } from "vue-router";

type NaiveTableColumn<T> = DataTableColumn<T> & { key: keyof T; title: string };

export const filterFunctions: Record<FilterType, (value: any, ...args: any) => boolean> = {
    freetext: (value: string, pattern: string) => {
        const regexPattern = pattern
            .split("*")
            .map((part) => _.escapeRegExp(part))
            .join(".*");

        return new RegExp(`^${regexPattern}$`).test(value);
    },
    options: (value: string | number | boolean, selected: string[]) => {
        return _.includes(selected, String(value));
    },
    datetime: (value: string | Date, range: [number | undefined, number | undefined]) => {
        const timestamp = new Date(value).getTime();
        const [before, after] = range;

        return (before === undefined || timestamp >= before) && (after === undefined || timestamp <= after);
    },
    range: (value: number, range: [number | undefined, number | undefined]) => {
        const [min, max] = range;

        return (min === undefined || value >= min) && (max === undefined || value <= max);
    },
};

export const formatFilterText = <T>(
    key: keyof T,
    value: string | string[] | [undefined | number, undefined | number],
    columns: DataTableColumns<T>,
    filterConfig: FilterConfig<T>,
) => {
    const column = _.find(
        columns,
        (col): col is NaiveTableColumn<T> => "key" in col && col.key === key && "title" in col && typeof col.title === "string",
    );

    if (!column || !filterConfig[key]) return `${String(key)}: ${value}`;

    const title = filterConfig[key]?.label ?? column.title;

    if (filterConfig[key]?.type === "freetext") {
        return `${title} matching: ${value}`;
    }

    if (filterConfig[key]?.type === "options") {
        const dict: Record<string | number, string> = _.mapValues(_.keyBy(filterConfig[key]?.options, "value"), "label");
        const values = [value].flat() as string[];
        const labels = values.map((v) => dict[v]);

        return `${title}: ${labels.join(", ")}`;
    }

    if (filterConfig[key]?.type === "datetime") {
        const [after, before] = value as RangeValue;

        if (!after && !before) return "";

        if (!before) return `${title} after: ${new Date(Number(after)).toLocaleString()}`;
        if (!after) return `${title} before: ${new Date(Number(before)).toLocaleString()}`;

        return `${title} between: ${new Date(Number(after)).toLocaleString()} - ${new Date(Number(before)).toLocaleString()}`;
    }

    if (filterConfig[key]?.type === "range") {
        const [min, max] = value as RangeValue;

        if (!min && !max) return "";

        if (!min) return `${title} less or equal: ${max}`;
        if (!max) return `${title} greater or equal: ${min}`;

        return `${title} between ${min} - ${max}`;
    }
};

export const getFiltersFromQuery = <T extends Record<string, any>>(query: LocationQuery, filterConfig: FilterConfig<T>) => {
    const filters: Record<string, string | string[] | RangeValue> = {};

    _.entries(query).forEach(([key, value]) => {
        if (_.isNil(value)) return;

        const config = filterConfig[key];

        if (config?.type === "freetext" && _.isString(value)) {
            filters[key] = value;
            return;
        }

        if (config?.type === "options") {
            filters[key] = _.castArray(value).filter((e) => !_.isNil(e));
            return;
        }

        // min value in range/datetime
        if (key.endsWith("_min") && !isNaN(_.parseInt(value as string))) {
            const keyWithoutSuffix = key.slice(0, -4);
            const config = filterConfig[keyWithoutSuffix];

            if (_.includes(["datetime", "range"], config?.type)) {
                filters[keyWithoutSuffix] = [Number(value), filters[keyWithoutSuffix]?.[1]] as RangeValue;
            }
        }

        // max value in range/datetime
        if (key.endsWith("_max") && !isNaN(_.parseInt(value as string))) {
            const keyWithoutSuffix = key.slice(0, -4);
            const config = filterConfig[keyWithoutSuffix];

            if (_.includes(["datetime", "range"], config?.type)) {
                filters[keyWithoutSuffix] = [filters[keyWithoutSuffix]?.[0], Number(value)] as RangeValue;
            }
        }
    });

    return filters;
};

export const convertFiltersToParams = <T extends Record<string, any>>(
    filters: Filters<T>,
    filterConfig: FilterConfig<T>,
): URLSearchParams => {
    const params = new URLSearchParams();

    _.forEach(filters, (value, key: keyof T) => {
        if (_.isEmpty(value)) return;

        switch (filterConfig[key]?.type) {
            case "freetext":
                return params.append(String(key), String(value));
            case "options":
                return _.forEach(value as string[], (item) => params.append(String(key), String(item)));
            case "datetime":
            case "range":
                if (value?.[0]) params.append(`${String(key)}_min`, String(value[0]));
                if (value?.[1]) params.append(`${String(key)}_max`, String(value[1]));
                return;
        }
    });

    return params;
};
