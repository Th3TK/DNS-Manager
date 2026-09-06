import type { DataTableColumns, DataTableSortState } from "naive-ui";

export type FilterType = "freetext" | "options";

export type FilterOption = {
    label: string;
    value: string | number;
};

export type FilterFieldConfig =
    | {
          type: "freetext";
          allowedCharacters?: string;
      }
    | {
          type: "options";
          options: FilterOption[];
      };

export type FilterConfig<T> = Partial<Record<keyof T, FilterFieldConfig>>;

export type Filters<T> = Partial<Record<keyof T, string | string[]>>;

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
