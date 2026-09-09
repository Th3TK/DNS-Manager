import { HttpStatusCode, type AxiosError } from "axios";
import type { DNSRecord } from "../types/api.types";
import { useErrorHandler } from "./useErrorHandler";
import { ref, type Ref } from "vue";
import { deleteRecord } from "../services/api";
import { useRouter } from "vue-router";
import _ from "lodash";

export const useRecordActions = (onDeleteSuccess?: () => void, onDeleteError?: (error: AxiosError) => void) => {
    const { handleError } = useErrorHandler();
    const router = useRouter();

    const deleteModalOpened = ref(false);
    const createModalOpened = ref(false);
    const editModalOpened = ref(false);

    const onNavigate = (record: DNSRecord) => {
        router.push({
            name: "RecordDetails",
            params: { name: record.zone_name, record_name: record.name, record_type: record.type },
        });
    };

    const onDelete = (records: DNSRecord[]) => {
        Promise.all(records.map((z) => deleteRecord(z.zone_name, z.name, z.type)))
            .then(onDeleteSuccess)
            .catch((error: AxiosError) => {
                if (error.response?.status !== HttpStatusCode.NotFound) {
                    handleError(error);
                }

                onDeleteError?.(error);
            });
    };

    return {
        deleteModalOpened,
        createModalOpened,
        editModalOpened,
        onDelete,
        onNavigate,
    };
};
