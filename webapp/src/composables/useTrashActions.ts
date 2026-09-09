import { ref } from "vue";
import { AxiosError, HttpStatusCode } from "axios";
import type { RestoreDNSRecordForm, TrashEntry } from "../types/api.types";
import { createZone, deleteTrashEntry, getZone, restoreTrashEntry } from "../services/api";
import { useErrorHandler } from "./useErrorHandler";
import { useRouter } from "vue-router";

export const useTrashActions = (
    onRestoreSuccess?: () => void,
    onRestoreError?: (error: AxiosError) => void,
    onDeleteSuccess?: () => void,
    onDeleteError?: (error: AxiosError) => void,
) => {
    const { handleError, displayErrorNotification } = useErrorHandler();

    const showCreateZoneConfirmation = ref(false);
    const showDeleteItemConfirmation = ref(false);

    const router = useRouter();

    const onNavigate = (entry: TrashEntry) => {
        router.push({ name: "TrashEntryDetails", params: { uuid: entry.entry_uuid } });
    };

    const restore = async (entry: TrashEntry) => {
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

    const onRestore = (entry: TrashEntry) => {
        if (entry.object_type !== "record") {
            return restore(entry);
        }

        getZone(entry.object_data.zone_name)
            .then(() => restore(entry))
            .catch((error: AxiosError) => {
                if (error.response?.status === HttpStatusCode.NotFound) {
                    showCreateZoneConfirmation.value = true;
                    return;
                }

                handleError(error);
            });
    };

    const onCreateZoneAndRestore = (entry: TrashEntry) => {
        showCreateZoneConfirmation.value = false;

        createZone({
            name: (entry.object_data as RestoreDNSRecordForm).zone_name,
            comment: "Automatically created during record restoration.",
        })
            .then(() => restore(entry))
            .catch(handleError);
    };

    const onDelete = (entries: TrashEntry[]) => {
        Promise.all(entries.map((e) => deleteTrashEntry(e.entry_uuid)))
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
