<script setup lang="ts">
import { AxiosError } from "axios";

import type { User } from "../../types/api.types.ts";

import { computed, toRef } from "vue";
import _ from "lodash";
import ConfirmationModal from "../modals/ConfirmationModal.vue";
import { NText } from "naive-ui";
import { useUserActions } from "../../composables/useUserActions.ts";
import UserDropdownControls from "./user/UserDropdownControls.vue";
import UserTableControls from "./user/UserTableControls.vue";
import CreateUserModal from "../modals/CreateUserModal.vue";
import ChangePasswordModal from "../modals/ChangePasswordModal.vue";
import EditUserModal from "../modals/EditUserModal.vue";
import CurrentUserControls from "./user/CurrentUserControls.vue";

defineOptions({
    inheritAttrs: false,
});

const props = defineProps<{
    users: User | User[];
    type: "dropdown" | "current" | "table";
    onDeleteError?: (error: AxiosError) => void;
    onDeleteSuccess?: () => void;
    onCreateSuccess?: (record: User) => void;
    onEditSuccess?: (record: User) => void;
}>();

const users = toRef(props, "users");
const { createModalOpened, deleteModalOpened, editModalOpened, changePasswordModalOpened, onDelete, onLogout } = useUserActions(
    users,
    props.onDeleteSuccess,
    props.onDeleteError,
);

const isSingleUser = computed(() => !_.isArray(users.value) || users.value.length === 1);
const userList = computed(() => [users.value].flat());
const user = computed(() => (isSingleUser.value ? userList.value[0] : null));
</script>
<template>
    <UserDropdownControls
        v-if="type === 'dropdown' && isSingleUser"
        v-bind="$attrs"
        @edit="editModalOpened = true"
        @delete="deleteModalOpened = true"
        @change-password="changePasswordModalOpened = true"
    />

    <UserTableControls
        v-if="type === 'table' && _.isArray(users)"
        v-bind="$attrs"
        :show-delete="Boolean(users.length)"
        @delete="deleteModalOpened = true"
        @create="createModalOpened = true"
    />
    <CurrentUserControls
        v-if="type === 'current' && user"
        v-bind="$attrs"
        :user="user"
        @logout="onLogout"
        @change-password="changePasswordModalOpened = true"
    />
    <ConfirmationModal
        type="error"
        v-model:show="deleteModalOpened"
        @submit="onDelete"
    >
        <template #title> User{{ isSingleUser ? "" : "s" }} deletion </template>

        <template #description>
            <NText v-if="!isSingleUser">
                Selected users ({{ userList.length }}) will be
                <NText>permanently deleted. This action cannot be undone.</NText>
            </NText>
            <NText v-else> Selected user will be permanently deleted. This action cannot be undone. </NText>
        </template>
    </ConfirmationModal>
    <CreateUserModal
        v-model:show="createModalOpened"
        @submit="onCreateSuccess"
    />
    <ChangePasswordModal
        v-if="user"
        v-model:show="changePasswordModalOpened"
        :username="user?.username"
        :current-user="type === 'current'"
    />
    <EditUserModal
        v-if="user"
        :user="user"
        v-model:show="editModalOpened"
        @submit="onEditSuccess"
    />
</template>
