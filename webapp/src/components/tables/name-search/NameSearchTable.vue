<script setup lang="ts">
import { ListSearch, Search } from "@vicons/tabler";
import { columns } from "./columns.ts";
import { NButton, NDataTable, NFlex, NForm, NIcon, NInput, NText, type PaginationInfo } from "naive-ui";
import { ref } from "vue";
import { nameSearch } from "../../../services/api.ts";
import type { NameSearchDNSRecord } from "../../../types/api.types.ts";
import { sanitizeNameSearchValue } from "../../../utils/dns.ts";
import { useErrorHandler } from "../../../composables/useErrorHandler.ts";
import type { AxiosError } from "axios";
import type { TableRow } from "../../../types/table.types.ts";
import _ from "lodash";
import { useRouter } from "vue-router";
import BaseDataTable from "../../data-table/BaseDataTable.vue";
import { h } from "vue";

const { handleError } = useErrorHandler();
const router = useRouter();

const data = ref<NameSearchDNSRecord[]>([]);
const error = ref(false);
const loading = ref(false);
const searched = ref<boolean>(false);

const input = ref<string>("");

const onChange = (value: string) => {
    searched.value = false;
    input.value = sanitizeNameSearchValue(value);
};

const handleClick = (row: NameSearchDNSRecord) =>
    router.push(
        row.location === "active"
            ? {
                  name: "RecordDetails",
                  params: {
                      name: row.zone_name,
                      record_name: row.name,
                      record_type: row.type,
                  },
              }
            : {
                  name: "TrashEntryDetails",
                  params: {
                      uuid: row.trash_entry_uuid,
                  },
              },
    );

const search = async () => {
    if (!input.value) return;
    loading.value = true;
    error.value = false;
    searched.value = true;

    nameSearch(input.value)
        .then((val) => {
            data.value = val;
        })
        .catch((err: AxiosError) => {
            error.value = true;
            data.value = [];
            handleError(err);
        })
        .finally(() => {
            loading.value = false;
        });
};
</script>

<template>
    <NFlex
        vertical
        class="container"
        size="large"
    >
        <NForm @submit.prevent="search">
            <NFlex>
                <NInput
                    maxlength="253"
                    placeholder="*.example.com"
                    class="name-search-input"
                    :value="input"
                    :loading="loading"
                    @update:value="onChange"
                >
                    <template #prefix>
                        <NIcon :component="ListSearch" />
                    </template>
                </NInput>
                <NButton
                    type="primary"
                    secondary
                    attr-type="submit"
                    icon-placement="right"
                >
                    <template #icon>
                        <NIcon
                            :component="Search"
                            size="16"
                        />
                    </template>
                    Search
                </NButton>
            </NFlex>
        </NForm>
        <NText
            v-if="error"
            depth="3"
        >
            Result:
            <NText type="error">Error</NText>
        </NText>
        <NText
            depth="3"
            v-else-if="loading"
        >
            Loading...
        </NText>
        <NText
            depth="3"
            v-else-if="searched || data.length"
        >
            Result:
            <NText :type="data.length ? 'warning' : 'primary'">
                {{ data.length ? "Taken" : "Free" }}
            </NText>
        </NText>
        <BaseDataTable
            v-if="data.length"
            :data="data"
            :row-keys="['zone_name', 'name', 'type', 'trash_entry_uuid']"
            :columns="columns"
            :loading="loading"
            :pagination-prefix="
                ({ itemCount }: PaginationInfo) =>
                    h(
                        NText,
                        {
                            depth: 3,
                            strong: true,
                        },
                        {
                            default: () => `Found ${itemCount ?? 0} record${itemCount && itemCount > 1 ? 's' : ''}`,
                        },
                    )
            "
            ,
            @cell-click="handleClick"
        />
    </NFlex>
</template>

<style scoped>
.container {
    height: 100%;
}
.name-search-input {
    max-width: 700px;
}
.data-table {
    flex: 1;
}

:deep(.n-pagination) {
    width: 100%;
}
:deep(.n-pagination-prefix) {
    flex: 1 !important;
    font-size: 15px;
}
</style>
