<script setup lang="ts">
import { ListSearch, Search } from "@vicons/tabler";
import { columns } from "./columns.ts";
import { NButton, NDataTable, NFlex, NForm, NIcon, NInput, NText, type PaginationInfo } from "naive-ui";
import { h, ref } from "vue";
import { nameSearch } from "../../../services/api.ts";
import type { NameSearchDNSRecord } from "../../../types/api.types.ts";
import { sanitizeNameSearchValue } from "../../../services/dns.ts";
import { useErrorHandler } from "../../../composables/useErrorHandler.ts";
import type { AxiosError } from "axios";
import type { TableRow } from "../../../types/table.types.ts";
import _ from "lodash";
import TextField from "../../data-table/fields/TextField.vue";

const { handleError } = useErrorHandler();

const data = ref<TableRow<NameSearchDNSRecord>[]>([]);
const error = ref(false);
const loading = ref(false);

const lastSearch = ref<string | null>(null);
const input = ref<string>("");

const onChange = (value: string) => {
    console.log(value, sanitizeNameSearchValue(value));
    input.value = sanitizeNameSearchValue(value);
};

const search = async () => {
    if (!input.value || input.value === lastSearch.value) return;
    loading.value = true;
    error.value = false;

    nameSearch(input.value)
        .then((val) => {
            data.value = _.map(val, (r: NameSearchDNSRecord, i) => ({ ...r, key: `${i}` }));
            lastSearch.value = input.value;
        })
        .catch((err: AxiosError) => {
            lastSearch.value = null;
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
            depth="3"
            v-if="loading"
        >
            Loading...
        </NText>
        <NText
            depth="3"
            v-if="error || (lastSearch && !loading)"
        >
            Result:
            <NText
                depth="1"
                :type="error ? 'error' : data.length ? 'warning' : 'primary'"
            >
                {{ error ? "Error" : data.length ? "Taken" : "Free" }}
            </NText>
        </NText>
        <NDataTable
            v-if="data.length"
            :columns="columns"
            :data="data"
            :loading="loading"
            :pagination="{
                showSizePicker: true,
                pageSizes: [10, 25, 50, 100],
                prefix: ({ itemCount }: PaginationInfo) => `Found ${itemCount} records`,
            }"
            striped
            flex-height
            class="data-table"
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

.data-table :deep(.n-pagination) {
    width: 100%;
}
.data-table :deep(.n-pagination-prefix) {
    flex: 1 !important;
    font-size: 16px;
}
</style>
