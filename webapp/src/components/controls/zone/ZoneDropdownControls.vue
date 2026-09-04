<script setup lang="ts">
import { DotsVertical, FileText, Trash } from "@vicons/tabler";
import { h } from "vue";
import { NButton, NDropdown, NIcon, type DropdownOption } from "naive-ui";

const emit = defineEmits<{
    navigate: [];
    delete: [];
}>();

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
            @dblclick.stop
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
