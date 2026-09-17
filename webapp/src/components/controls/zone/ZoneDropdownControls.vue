<script setup lang="ts">
import { DotsVertical, FileText, Trash } from "@vicons/tabler";
import { h } from "vue";
import { NButton, NDropdown, NIcon, type DropdownOption } from "naive-ui";
import { useAuthenticationStore } from "../../../stores/useAuthenticationStore";

const emit = defineEmits<{
    navigate: [];
    delete: [];
}>();

const authentication = useAuthenticationStore();

const options: DropdownOption[] = [
    {
        label: "View zone details",
        key: "navigate",
        icon: () => h(NIcon, { component: FileText }),
    },
    {
        label: "Delete",
        key: "delete",
        icon: () => h(NIcon, { component: Trash }),
        disabled: !authentication.isAdmin,
    },
];

const onSelect = (key: string | number) => {
    switch (key) {
        case "navigate":
            emit("navigate");
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
            :focusable="false"
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
