<script setup lang="ts">
import { ArrowBackUp } from "@vicons/tabler";
import { AxiosError, HttpStatusCode } from "axios";
import { NButton, NFlex, NIcon } from "naive-ui";
import { ref } from "vue";
import type { RestoreDNSRecordForm, TrashEntry } from "../../../types/api.types";
import { createZone, getZone, restoreTrashEntry } from "../../../services/api.ts";
import { useErrorHandler } from "../../../composables/useErrorHandler.ts";
import ConfirmationModal from "../../modals/ConfirmationModal.vue";

const props = defineProps<{
    entry: TrashEntry;
    refresh?: () => void;
}>();

const { handleError, displayErrorNotification } = useErrorHandler();

const showCreateZoneConfirmation = ref(false);
const restoring = ref(false);

const restore = async () => {
    await restoreTrashEntry(props.entry.entry_uuid)
        .catch((error: AxiosError) => {
            if (error instanceof AxiosError && error.response?.status === HttpStatusCode.Conflict) {
                return displayErrorNotification(
                    `Duplicate ${props.entry.object_type}`,
                    props.entry.object_type === "zone"
                        ? "A zone with the same name already exists."
                        : "A record with the same name and type already exists.",
                );
            }

            return handleError(error);
        })
        .finally(props.refresh);
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
    restoring.value = true;

    createZone({
        name: (props.entry.object_data as RestoreDNSRecordForm).zone_name,
        comment: "Automatically created during record restoration.",
    })
        .then(restore)
        .catch(handleError)
        .finally(() => {
            restoring.value = true;
        });
};
</script>

<template>
    <NFlex
        class="container"
        @dblclick.stop
    >
        <NButton
            type="info"
            tertiary
            :loading="restoring"
            @click="onRestore"
        >
            <template #icon>
                <NIcon :component="ArrowBackUp" />
            </template>

            Restore
        </NButton>
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
</template>

<style scoped>
.container {
    width: 100%;
    justify-content: center !important;
}
</style>
