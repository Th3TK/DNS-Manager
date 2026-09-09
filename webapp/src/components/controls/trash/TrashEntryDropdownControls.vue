<script setup lang="ts">
import { ArrowBackUp, ChevronRight, DotsVertical, FileText, Link, TrashX } from "@vicons/tabler";
import { h } from "vue";
import { NButton, NDropdown, NIcon, type DropdownOption } from "naive-ui";
import _ from "lodash";

const emit = defineEmits<{
    navigate: [];
    restore: [];
    delete: [];
}>();

const options: DropdownOption[] = [
    {
        label: "View item details",
        key: "navigate",
        icon: () => h(NIcon, { component: FileText }),
    },
    {
        label: "Restore",
        key: "restore",
        icon: () => h(NIcon, { component: ArrowBackUp }),
    },
    {
        label: "Delete permanently",
        key: "delete",
        icon: () => h(NIcon, { component: TrashX }),
    },
];

const onSelect = (key: string | number) => {
    switch (key) {
        case "navigate":
            emit("navigate");
            break;
        case "restore":
            emit("restore");
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
