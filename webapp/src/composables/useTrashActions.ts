import { ref } from "vue";
import { AxiosError, HttpStatusCode } from "axios";
import type { RestoreDNSRecordForm, TrashEntry } from "../types/api.types";
import { createZone, deleteTrashEntry, getZone, restoreTrashEntry } from "../services/api";
import { useErrorHandler } from "./useErrorHandler";
import { useRouter } from "vue-router";

export const useTrashActions = (
    entry: TrashEntry,
    onRestoreSuccess?: () => void,
    onRestoreError?: (error: AxiosError) => void,
    onDeleteSuccess?: () => void,
    onDeleteError?: (error: AxiosError) => void,
) => {
    const { handleError, displayErrorNotification } = useErrorHandler();

    const showCreateZoneConfirmation = ref(false);
    const showDeleteItemConfirmation = ref(false);

    const router = useRouter();

    const onNavigate = () => {
        router.push({ name: "TrashEntryDetails", params: { uuid: entry.entry_uuid } });
    };

    const restore = async () => {
        await restoreTrashEntry(entry.entry_uuid)
            .then(onRestoreSuccess)
            .catch((error: AxiosError) => {
                if (error.response?.status === HttpStatusCode.Conflict) {
                    displayErrorNotification(
                        `Duplicate ${entry.object_type}`,
                        entry.object_type === "zone"
                            ? "A zone with the same name already exists."
                            : "A record with the same name and type already exists.",
                    );
                } else {
                    handleError(error);
                }

                onRestoreError?.(error);
            });
    };

    const onRestore = () => {
        if (entry.object_type !== "record") {
            return restore();
        }

        getZone(entry.object_data.zone_name)
            .then(restore)
            .catch((error: AxiosError) => {
                if (error.response?.status === HttpStatusCode.NotFound) {
                    showCreateZoneConfirmation.value = true;
                    return;
                }

                handleError(error);
            });
    };

    const onCreateZoneAndRestore = () => {
        showCreateZoneConfirmation.value = false;

        createZone({
            name: (entry.object_data as RestoreDNSRecordForm).zone_name,
            comment: "Automatically created during record restoration.",
        })
            .then(restore)
            .catch(handleError);
    };

    const onDelete = () => {
        deleteTrashEntry(entry.entry_uuid)
            .then(onDeleteSuccess)
            .catch((error: AxiosError) => {
                if (error.response?.status !== HttpStatusCode.NotFound) {
                    handleError(error);
                }

                onDeleteError?.(error);
            });
    };

    return {
        showCreateZoneConfirmation,
        showDeleteItemConfirmation,
        onRestore,
        onCreateZoneAndRestore,
        onDelete,
        onNavigate,
    };
};
