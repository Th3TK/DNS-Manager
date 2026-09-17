<script setup lang="ts">
import { AxiosError } from "axios";

import type { User } from "../../types/api.types.ts";

import { computed, ref, toRef } from "vue";
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
    onDeleteError?: (error?: AxiosError) => void;
    onDeleteSuccess?: () => void;
    onCreateSuccess?: (record: User) => void;
    onEditSuccess?: (record: User) => void;
}>();

const users = toRef(props, "users");

const changePasswordModalOpened = ref(false);
const deleteModalOpened = ref(false);
const createModalOpened = ref(false);
const editModalOpened = ref(false);

const { onDelete, onLogout } = useUserActions(props.onDeleteSuccess, props.onDeleteError);

const usersList = computed(() => [users.value].flat());
const user = computed(() => (_.isArray(users.value) ? null : users.value));
</script>
<template>
    <UserDropdownControls
        v-if="type === 'dropdown' && user"
        v-bind="$attrs"
        @edit="editModalOpened = true"
        @delete="deleteModalOpened = true"
        @change-password="changePasswordModalOpened = true"
    />
    <CurrentUserControls
        v-else-if="type === 'current' && user"
        v-bind="$attrs"
        :user="user"
        @logout="onLogout"
        @change-password="changePasswordModalOpened = true"
    />

    <UserTableControls
        v-else-if="type === 'table'"
        v-bind="$attrs"
        :show-delete="Boolean(usersList.length)"
        @delete="deleteModalOpened = true"
        @create="createModalOpened = true"
    />
    <ConfirmationModal
        type="error"
        v-model:show="deleteModalOpened"
        @submit="() => onDelete(usersList)"
    >
        <template #title> User{{ user ? "" : "s" }} deletion </template>

        <template #description>
            <NText v-if="!user">
                Selected users ({{ usersList.length }}) will be
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
