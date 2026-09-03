<script setup lang="ts">
import { ArrowBackUp, DotsVertical, TrashX } from "@vicons/tabler";
import { AxiosError, HttpStatusCode } from "axios";
import { NButton, NDropdown, NFlex, NIcon, type DropdownOption } from "naive-ui";
import { h, ref } from "vue";
import type { RestoreDNSRecordForm, TrashEntry } from "../../types/api.types.ts";
import { createZone, deleteTrashEntry, getZone, restoreTrashEntry } from "../../services/api.ts";
import { useErrorHandler } from "../../composables/useErrorHandler.ts";
import ConfirmationModal from "../modals/ConfirmationModal.vue";

const props = defineProps<{
    entry: TrashEntry;
    dropdown?: boolean;
    onRestoreError?: (error: AxiosError) => void;
    onRestoreSuccess?: () => void;
    onDeleteError?: (error: AxiosError) => void;
    onDeleteSuccess?: () => void;
}>();

const { handleError, displayErrorNotification } = useErrorHandler();

const showCreateZoneConfirmation = ref(false);
const showDeleteItemConfirmation = ref(false);

const restore = async () => {
    await restoreTrashEntry(props.entry.entry_uuid)
        .then(props.onRestoreSuccess)
        .catch((error: AxiosError) => {
            if (error.response?.status === HttpStatusCode.Conflict) {
                displayErrorNotification(
                    `Duplicate ${props.entry.object_type}`,
                    props.entry.object_type === "zone"
                        ? "A zone with the same name already exists."
                        : "A record with the same name and type already exists.",
                );
            } else handleError(error);
            return props.onRestoreError?.(error);
        });
};

const onRestore = () => {
    if (props.entry.object_type !== "record") {
        return restore();
    }

    const zoneName = props.entry.object_data.zone_name;

    getZone(zoneName)
        // if zone exists then restore
        .then(restore)
        .catch((error: AxiosError) => {
            // if it doesn't, show a prompt
            if (error.response?.status === HttpStatusCode.NotFound) {
                return (showCreateZoneConfirmation.value = true);
            }
            // handle any other errors
            return handleError(error);
        });
};

const onCreateZoneAndRestore = async () => {
    showCreateZoneConfirmation.value = false;

    createZone({
        name: (props.entry.object_data as RestoreDNSRecordForm).zone_name,
        comment: "Automatically created during record restoration.",
    })
        .then(restore)
        .catch(handleError);
};

const onDelete = () => {
    deleteTrashEntry(props.entry.entry_uuid)
        .then(props.onDeleteSuccess)
        .catch((error) => {
            if (error.response?.status !== HttpStatusCode.NotFound) handleError(error);
            props.onDeleteError?.(error);
        });
};

const dropdownOptions: DropdownOption[] = [
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

const onDropdownSelect = (key: string | number) => {
    switch (key) {
        case "restore":
            onRestore();
            break;

        case "delete":
            showDeleteItemConfirmation.value = true;
            break;
    }
};
</script>

<template>
    <NDropdown
        v-if="dropdown"
        :options="dropdownOptions"
        @select="onDropdownSelect"
        trigger="click"
        :show-arrow="true"
        @dblclick.stop
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

    <NFlex v-else>
        <NFlex
            class="container"
            @dblclick.stop
        >
            <NButton
                type="info"
                tertiary
                @click="onRestore"
                strong
            >
                <template #icon>
                    <NIcon :component="ArrowBackUp" />
                </template>
                Restore
            </NButton>
        </NFlex>
        <NFlex
            class="container"
            @dblclick.stop
        >
            <NButton
                type="error"
                tertiary
                @click="showDeleteItemConfirmation = true"
                strong
            >
                <template #icon>
                    <NIcon :component="TrashX" />
                </template>
                Delete permanently
            </NButton>
        </NFlex>
    </NFlex>

    <ConfirmationModal
        type="primary"
        v-model:show="showCreateZoneConfirmation"
        @submit="onCreateZoneAndRestore"
    >
        <template #title> Creating missing zone </template>

        <template #description>
            The zone for this record no longer exists. A new zone will be created automatically along with the restored record.
        </template>
    </ConfirmationModal>
    <ConfirmationModal
        type="error"
        v-model:show="showDeleteItemConfirmation"
        @submit="onDelete"
    >
        <template #title> Permanent item deletion </template>

        <template #description> This item will be permanently deleted. This action cannot be undone. </template>
    </ConfirmationModal>
</template>

<style scoped>
.container {
    justify-content: center !important;
}
.icon-button {
    aspect-ratio: 1/1;
    padding: 0;
    cursor: pointer !important;
}
</style>
