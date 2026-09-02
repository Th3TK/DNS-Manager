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
import DeleteConfirmationModal from "../../modals/DeleteConfirmationModal.vue";
import type { TableExpose } from "../../../types/table.types.ts";

const { data: users } = useFetch<User[]>("/users");

const table = useTemplateRef<TableExpose<DNSZone>>("table");
const selectedKeys = ref<DataTableRowKey[]>([]);
const openedCreateModal = ref(false);
const openedDeleteModal = ref(false);

const router = useRouter();
const handleClick = (row: DNSZone) => router.push(`/zones/${row.name}`);

const filterConfig = computed(() => getFilterConfig(users.value ?? []));

const selectedZone = computed(() => table.value?.selectedRows[0]);
const isSelectedExternal = computed(() => selectedZone.value && selectedZone.value.origin === "external");

const deleteSelected = async () => {
    if (!selectedZone.value) return;
    await deleteZone(selectedZone.value.name);
    table.value?.refresh();
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
                    Zone list
                    <NText depth="3"> ({{ table?.total ?? 0 }}) </NText>
                </NText>
                <NText depth="3"> Click on a zone to view its full details and records. </NText>
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
            <DeleteConfirmationModal
                v-model:show="openedDeleteModal"
                @delete="deleteSelected"
            >
                <template #title> Zone {{ isSelectedExternal ? "permanent " : "" }}deletion </template>
                <template #description>
                    <NText>
                        Selected zone will be {{ isSelectedExternal ? "permanently deleted" : "moved to trash" }} along with
                        <NText type="error"> all of its records ({{ selectedZone?.record_count }}). </NText>
                    </NText>
                    <NText v-if="isSelectedExternal">This action cannot be undone.</NText>
                </template>
            </DeleteConfirmationModal>

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
                :on-submit="table?.refresh"
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
