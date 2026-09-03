<script setup lang="ts">
import { type User, type DNSZone } from "../../../types/api.types.ts";
import { type DataTableRowKey, NButton, NFlex, NIcon, NText } from "naive-ui";
import { computed, ref, shallowRef, Text, useTemplateRef } from "vue";
import { Plus as IconPlus, Trash as IconTrash } from "@vicons/tabler";
import { useRouter } from "vue-router";
import useFetch from "../../../composables/useFetch.ts";
import { columns } from "./columns.ts";
import { deleteZone, getZones } from "../../../services/api.ts";
import ClientDataTable from "../../data-table/ClientDataTable.vue";
import { getFilterConfig } from "./filters.ts";
import CreateZoneModal from "../../modals/CreateZoneModal.vue";
import ConfirmationModal from "../../modals/ConfirmationModal.vue";
import type { TableExpose } from "../../../types/table.types.ts";
import { useErrorHandler } from "../../../composables/useErrorHandler.ts";
import { HttpStatusCode } from "axios";

const { data: users } = useFetch<User[]>("/users");
const { handleError } = useErrorHandler();

const table = useTemplateRef<TableExpose<DNSZone>>("table");
const selectedKeys = ref<DataTableRowKey[]>([]);
const openedCreateModal = ref(false);
const openedDeleteModal = ref(false);

const router = useRouter();
const handleClick = (row: DNSZone) => router.push(`/zones/${row.name}`);

const filterConfig = computed(() => getFilterConfig(users.value ?? []));

const selectedZone = computed(() => table.value?.selectedRows[0]);

const deleteSelected = async () => {
    if (!selectedZone.value) return;
    deleteZone(selectedZone.value.name)
        .catch((error) => {
            if (error.response?.status === HttpStatusCode.NotFound) return;
            handleError(error);
        })
        .finally(() => table.value?.refresh());
};
</script>

<template>
    <ClientDataTable
        ref="table"
        v-model:selected-keys="selectedKeys"
        :rowKeys="['name']"
        :get-data="getZones"
        :columns="columns"
        :onCellClick="handleClick"
        :filterConfig="filterConfig"
    >
        <template #header>
            <NFlex
                vertical
                :size="0"
                class="header"
            >
                <NText
                    tag="h1"
                    class="title"
                >
                    Zone List
                    <NText depth="3"> ({{ table?.total ?? 0 }}) </NText>
                </NText>
                <NText depth="3"> Double click on a zone to view its full details and records. </NText>
            </NFlex>
        </template>
        <template #controls>
            <NButton
                type="error"
                strong
                v-if="selectedKeys.length"
                @click="openedDeleteModal = true"
            >
                <template #icon>
                    <NIcon
                        :component="IconTrash"
                        size="16"
                    />
                </template>
                Delete Zone
            </NButton>
            <ConfirmationModal
                type="error"
                v-model:show="openedDeleteModal"
                @submit="deleteSelected"
            >
                <template #title> Zone deletion </template>
                <template #description>
                    <NText>
                        Selected zone will be deleted along with
                        <NText type="error"> all of its records ({{ selectedZone?.record_count }}). </NText>
                    </NText>
                    <NText>
                        The zone and its internal records will be moved to trash, while
                        <NText type="error">external records will be permanently deleted.</NText>
                    </NText>
                </template>
            </ConfirmationModal>

            <NButton
                type="primary"
                strong
                @click="openedCreateModal = true"
            >
                <template #icon>
                    <NIcon
                        :component="IconPlus"
                        size="16"
                    />
                </template>
                Create Zone
            </NButton>
            <CreateZoneModal
                v-model:show="openedCreateModal"
                @submit="table?.refresh"
            />
        </template>
    </ClientDataTable>
</template>

<style lang="css" scoped>
.header {
    padding-bottom: var(--spacing-md);
}

.title {
    line-height: normal;
    margin-top: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
}
</style>
