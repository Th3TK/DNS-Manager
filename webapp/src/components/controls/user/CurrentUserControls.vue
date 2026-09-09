<script setup lang="ts">
import { ChevronRight, Key, Logout, User as UserIcon, UserCircle } from "@vicons/tabler";
import { NBadge, NButton, NDropdown, NFlex, NIcon, NTag, NText, type DropdownOption } from "naive-ui";
import { h, ref } from "vue";
import type { User } from "../../../types/api.types";
import { logout } from "../../../services/api";
import { useRouter } from "vue-router";
import { useAuthenticationStore } from "../../../stores/useAuthenticationStore";

const props = defineProps<{
    user: User;
}>();

const emit = defineEmits(["change-password", "logout"]);

const authentication = useAuthenticationStore();
const router = useRouter();

const userMenuOptions: DropdownOption[] = [
    {
        label: "Change password",
        key: "change-password",
        icon: () =>
            h(NIcon, null, {
                default: () => h(Key),
            }),
    },
    {
        label: "Log out",
        key: "logout",
        icon: () =>
            h(NIcon, null, {
                default: () => h(Logout),
            }),
    },
];

const handleUserMenuSelect = (key: string) => {
    switch (key) {
        case "change-password":
            emit("change-password");
            break;
        case "logout":
            emit("logout");
            break;
    }
};
</script>

<template>
    <NDropdown
        trigger="click"
        :options="userMenuOptions"
        @select="handleUserMenuSelect"
        placement="right"
        show-arrow
    >
        <NButton
            class="user-button"
            quaternary
            icon-placement="right"
            :focusable="false"
        >
            <NFlex class="user-card">
                <NIcon
                    size="24"
                    :component="UserIcon"
                />
                <NFlex
                    class="user-details"
                    vertical
                >
                    <NText
                        class="full-name"
                        ellipsis
                    >
                        {{ user.full_name || `${user.username}` }}
                    </NText>

                    <NText
                        class="username"
                        depth="3"
                        ellipsis
                    >
                        {{ `${user.username}` }}
                    </NText>
                </NFlex>
            </NFlex>
            <template #icon>
                <NIcon
                    :component="ChevronRight"
                    size="16"
                />
            </template>
        </NButton>
    </NDropdown>
</template>

<style scoped>
.user-button {
    width: 100%;
    box-sizing: border-box;
    height: 52px;
    padding: var(--spacing-sm) var(--spacing-md) !important;
}

.user-button > * {
    flex: 1;
}

.user-card {
    display: flex;
    width: 100%;
    gap: var(--spacing-sm) !important;
    align-items: center;

    box-sizing: border-box;
}

.user-details {
    min-width: 0;
    flex: 1;
    gap: 0px !important;
    align-items: start;
}

.full-name,
.username {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 1.2;
    max-width: 100%;
}

.full-name {
    font-size: 15px;
}

.username {
    font-size: 13px;
}
</style>
