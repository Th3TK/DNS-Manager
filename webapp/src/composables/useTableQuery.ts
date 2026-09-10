import { onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import type { DataTableSortState } from "naive-ui";
import type { FilterConfig, Filters } from "../types/table.types";
import _, { filter, keyBy } from "lodash";
import { prepareTableParams } from "../services/api";
import { getFiltersFromQuery } from "../utils/filters";

export function useTableQuery<T extends Record<string, any>>(filterConfig: FilterConfig<T>) {
    const route = useRoute();
    const router = useRouter();

    const filters = ref<Filters<T>>({} as Filters<T>);
    const sorter = ref<DataTableSortState | null>(null);
    const page = ref(1);
    const pageSize = ref(25);

    const loadFromQuery = () => {
        route.query;

        filters.value = getFiltersFromQuery(route.query, filterConfig);

        page.value = Number(route.query.page) || 1;
        pageSize.value = Number(route.query.size) || 25;

        const sortQueriesPresent = route.query.sortBy && route.query.sortOrder;

        sorter.value = sortQueriesPresent
            ? ({
                  columnKey: route.query.sortBy,
                  order: route.query.sortOrder,
              } as DataTableSortState)
            : null;
    };

    const saveToQuery = async () => {
        const params = prepareTableParams(
            page.value,
            pageSize.value,
            filters.value,
            filterConfig,
            sorter.value?.columnKey as keyof T | undefined,
            sorter.value?.order as "ascend" | "descend" | undefined,
        );

        await router.replace({ query: Object.fromEntries(params.entries()) });
    };

    loadFromQuery();

    watch([filters, sorter, page, pageSize], saveToQuery, { deep: true });

    return {
        filters,
        sorter,
        page,
        pageSize,
    };
}
