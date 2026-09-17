<script setup lang="ts">
import { DotsVertical, Edit, FileText, Trash } from "@vicons/tabler";
import { computed, h } from "vue";
import { NButton, NDropdown, NIcon, type DropdownOption } from "naive-ui";
import { useAuthenticationStore } from "../../../stores/useAuthenticationStore";

const emit = defineEmits(["navigate", "edit", "delete"]);

const props = defineProps<{
    showEdit: boolean;
}>();

const authentication = useAuthenticationStore();

const options = computed<DropdownOption[]>(() => [
    {
        label: "View record details",
        key: "navigate",
        icon: () => h(NIcon, { component: FileText }),
    },
    ...(props.showEdit
        ? [
              {
                  label: "Edit",
                  key: "edit",
                  icon: () => h(NIcon, { component: Edit }),
                  disabled: !authentication.isAdmin,
              },
          ]
        : []),
    {
        label: "Delete",
        key: "delete",
        icon: () => h(NIcon, { component: Trash }),
        disabled: !authentication.isAdmin,
    },
]);

const onSelect = (key: string) => {
    switch (key) {
        case "navigate":
            emit("navigate");
            break;
        case "edit":
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
