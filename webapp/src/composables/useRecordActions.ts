import { HttpStatusCode, type AxiosError } from "axios";
import type { DNSRecord } from "../types/api.types";
import { useErrorHandler } from "./useErrorHandler";
import { ref, type Ref } from "vue";
import { deleteRecord } from "../services/api";
import { useRouter } from "vue-router";
import _ from "lodash";

export const useRecordActions = (
    records: Ref<DNSRecord | DNSRecord[]>,
    onDeleteSuccess?: () => void,
    onDeleteError?: (error: AxiosError) => void,
) => {
    const { handleError } = useErrorHandler();
    const router = useRouter();

    const deleteModalOpened = ref(false);
    const createModalOpened = ref(false);
    const editModalOpened = ref(false);

    const onNavigate = () => {
        if (_.isArray(records.value)) return;
        router.push({
            name: "RecordDetails",
            params: { name: records.value.zone_name, record_name: records.value.name, record_type: records.value.type },
        });
    };

    const onDelete = () => {
        Promise.all([records.value].flat().map((z) => deleteRecord(z.zone_name, z.name, z.type)))
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
