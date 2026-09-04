import { HttpStatusCode, type AxiosError } from "axios";
import type { DNSZone } from "../types/api.types";
import { useErrorHandler } from "./useErrorHandler";
import { ref, type Ref } from "vue";
import { deleteZone } from "../services/api";
import { useRouter } from "vue-router";
import _ from "lodash";

export const useZoneActions = (
    zones: Ref<DNSZone | DNSZone[]>,
    onDeleteSuccess?: () => void,
    onDeleteError?: (error: AxiosError) => void,
) => {
    const { handleError } = useErrorHandler();
    const router = useRouter();

    const deleteModalOpened = ref(false);
    const createModalOpened = ref(false);

    const onNavigate = () => {
        if (_.isArray(zones.value)) return;
        router.push({ name: "ZoneDetails", params: { name: zones.value.name } });
    };

    const onDelete = () => {
        Promise.all([zones.value].flat().map((z) => deleteZone(z.name)))
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
        onDelete,
        onNavigate,
    };
};
