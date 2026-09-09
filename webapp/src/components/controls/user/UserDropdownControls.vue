<script setup lang="ts">
import { DotsVertical, Edit, Key, Trash } from "@vicons/tabler";
import { h } from "vue";
import { NButton, NDropdown, NIcon, type DropdownOption } from "naive-ui";
import { useAuthenticationStore } from "../../../stores/useAuthenticationStore";

const emit = defineEmits(["change-password", "edit", "delete"]);

const authentication = useAuthenticationStore();

const options: DropdownOption[] = [
    {
        label: "Edit",
        key: "edit",
        icon: () => h(NIcon, { component: Edit }),
        disabled: !authentication.isAdmin,
    },
    {
        label: "Change Password",
        key: "change-password",
        icon: () => h(NIcon, { component: Key }),
        disabled: !authentication.isAdmin,
    },
    {
        label: "Delete",
        key: "delete",
        icon: () => h(NIcon, { component: Trash }),
        disabled: !authentication.isAdmin,
    },
];

const onSelect = (key: string) => {
    switch (key) {
        case "change-password":
            emit("change-password");
            break;
        case "edit":
            console.log("edit");
            emit("edit");
            break;
        case "delete":
            emit("delete");
            break;
    }
};
</script>

<template>
    <NDropdown
        :options="options"
        trigger="click"
        show-arrow
        @select="onSelect"
    >
        <NButton
            quaternary
            square
            class="icon-button"
            @click.stop
        >
            <NIcon
                :component="DotsVertical"
                :size="20"
            />
        </NButton>
    </NDropdown>
</template>

<style scoped>
.icon-button {
    aspect-ratio: 1;
    padding: 0;
}
</style>
