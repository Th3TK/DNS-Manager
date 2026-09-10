import type { DataTableColumns, DataTableSortState } from "naive-ui";

export type RangeValue = [number | undefined, number | undefined];

export type FilterType = "freetext" | "options" | "datetime" | "range";

export type FilterOption = {
    label: string;
    value: string | number;
};

export type FilterFieldConfig =
    | {
          type: "freetext";
          label?: string;
          allowedCharacters?: string;
      }
    | {
          type: "options";
          label?: string;
          options: FilterOption[];
      }
    | {
          type: "datetime";
          label?: string;
      }
    | {
          type: "range";
          label?: string;
          min?: number;
          max?: number;
      };

export type FilterConfig<T> = Partial<Record<keyof T, FilterFieldConfig>>;

export type Filters<T> = Partial<Record<keyof T, string | string[] | RangeValue>>;

export interface DataPaginated<T> {
    items: T[];
    total: number;
    page: number;
    size: number;
    pages: number;
}
export interface BaseDataTableExpose<T extends Record<string, any>> {
    page: number;
    pageSize: number;
    filters: Filters<T>;
    sorter: DataTableSortState | null;
    selectedRows: TableRow<T>[];
}

export interface TableExpose<T extends Record<string, any>> {
    total: number;
    refresh: () => Promise<void>;
    selectedRows: TableRow<T>[];
}

export type TableRow<T> = T & { key: string };
