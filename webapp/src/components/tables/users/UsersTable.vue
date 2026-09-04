<script setup lang="ts">
import { type User } from "../../../types/api.types.ts";
import { type DataTableRowKey, NButton, NFlex, NIcon, NText } from "naive-ui";
import { ref, useTemplateRef } from "vue";
import { Trash as IconTrash, UserPlus as IconUserPlus } from "@vicons/tabler";
import { columns } from "./columns.ts";
import { getUsers } from "../../../services/api.ts";
import ClientDataTable from "../../data-table/ClientDataTable.vue";
import CreateZoneModal from "../../modals/CreateZoneModal.vue";
import ConfirmationModal from "../../modals/ConfirmationModal.vue";
import type { TableExpose } from "../../../types/table.types.ts";
import { useErrorHandler } from "../../../composables/useErrorHandler.ts";
import { filters } from "./filters.ts";

const { handleError } = useErrorHandler();

const table = useTemplateRef<TableExpose<User>>("table");
const selectedKeys = ref<DataTableRowKey[]>([]);
const openedCreateModal = ref(false);
const openedDeleteModal = ref(false);

const deleteSelected = async () => {};
</script>

<template>
    <ClientDataTable
        ref="table"
        v-model:selected-keys="selectedKeys"
        :rowKeys="['username']"
        :get-data="getUsers"
        :columns="columns"
        :filterConfig="filters"
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
                    Users List
                    <NText depth="3"> ({{ table?.total ?? 0 }}) </NText>
                </NText>
                <NText depth="3"> Displays all accounts in the applicaton </NText>
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
                Delete User
            </NButton>
            <ConfirmationModal
                type="error"
                v-model:show="openedDeleteModal"
                @submit="deleteSelected"
            >
                <template #title> User deletion </template>
                <template #description>
                    <NText> Selected users ({{ selectedKeys.length }}) will be permanently deleted. This action cannot be undone. </NText>
                </template>
            </ConfirmationModal>

            <NButton
                type="primary"
                strong
                @click="openedCreateModal = true"
            >
                <template #icon>
                    <NIcon
                        :component="IconUserPlus"
                        size="16"
                    />
                </template>
                Create User
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
