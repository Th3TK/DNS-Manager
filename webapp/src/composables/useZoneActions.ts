import { HttpStatusCode, type AxiosError } from "axios";
import type { DNSZone } from "../types/api.types";
import { useErrorHandler } from "./useErrorHandler";
import { ref } from "vue";
import { deleteZone } from "../services/api";
import { useRouter } from "vue-router";

export const useZoneActions = (onDeleteSuccess?: () => void, onDeleteError?: (error: AxiosError) => void) => {
    const { handleError } = useErrorHandler();
    const router = useRouter();

    const deleteModalOpened = ref(false);
    const createModalOpened = ref(false);

    const onNavigate = (zone: DNSZone) => {
        router.push({ name: "ZoneDetails", params: { name: zone.name } });
    };

    const onDelete = (zones: DNSZone[]) => {
        Promise.all(zones.flat().map((z) => deleteZone(z.name)))
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
