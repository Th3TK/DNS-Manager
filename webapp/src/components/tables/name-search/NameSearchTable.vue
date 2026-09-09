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

const { handleError } = useErrorHandler();

const data = ref<TableRow<NameSearchDNSRecord>[]>([]);
const error = ref(false);
const loading = ref(false);
const searched = ref<boolean>(false);

const input = ref<string>("");

const onChange = (value: string) => {
    searched.value = false;
    input.value = sanitizeNameSearchValue(value);
};

const search = async () => {
    if (!input.value) return;
    loading.value = true;
    error.value = false;
    searched.value = true;

    nameSearch(input.value)
        .then((val) => {
            data.value = _.map(val, (r: NameSearchDNSRecord, i) => ({ ...r, key: `${i}` }));
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
            v-else-if="searched"
        >
            Result:
            <NText :type="data.length ? 'warning' : 'primary'">
                {{ data.length ? "Taken" : "Free" }}
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
                prefix: ({ itemCount }: PaginationInfo) => `Found ${itemCount ?? 0} record${itemCount && itemCount > 1 ? 's' : ''}`,
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
