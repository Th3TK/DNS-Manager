import type { DataTableColumns } from "naive-ui";

export type FilterType = "freetext" | "options";

export type FilterOption = {
    label: string;
    value: string;
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
