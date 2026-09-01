import { onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import type { DataTableSortState } from "naive-ui";
import type { Filters } from "../types/table.types";
import _, { filter, keyBy } from "lodash";

export function useTableQuery<T extends Record<string, any>>() {
    const route = useRoute();
    const router = useRouter();

    const filters = ref<Filters<T>>({} as Filters<T>);
    const sorter = ref<DataTableSortState | null>(null);
    const page = ref(1);
    const pageSize = ref(25);

    const loadFromQuery = () => {
        filters.value = {};

        _.entries(route.query).forEach(([key, value]) => {
            if (_.includes(["page", "pageSize", "sortBy", "sortOrder"], key)) return;

            if (_.isArray(value)) {
                filters.value[key] = value.filter((v) => !_.isNil(v));
                return;
            }

            if (!_.isNil(value)) {
                filters.value[key] = value;
            }
        });

        page.value = Number(route.query.page) || 1;
        pageSize.value = Number(route.query.pageSize) || 25;

        const sortQueriesPresent = route.query.sortBy && route.query.sortOrder;

        sorter.value = sortQueriesPresent
            ? ({
                  columnKey: route.query.sortBy,
                  order: route.query.sortOrder,
              } as DataTableSortState)
            : null;
    };

    const saveToQuery = async () => {
        const query: Record<string, string | string[]> = {
            page: String(page.value),
            pageSize: String(pageSize.value),
        };

        _.entries(filters.value).forEach(([key, value]) => {
            if (_.isEmpty(value)) return;
            query[key] = _.isArray(value) ? value.map(String) : String(value);
        });

        if (sorter.value?.columnKey && sorter.value.order) {
            query.sortBy = String(sorter.value.columnKey);
            query.sortOrder = sorter.value.order;
        }

        await router.replace({ query });
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
