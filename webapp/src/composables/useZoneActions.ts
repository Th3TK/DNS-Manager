import { HttpStatusCode, type AxiosError } from "axios";
import type { DNSZone } from "../types/api.types";
import { useErrorHandler } from "./useErrorHandler";
import { ref } from "vue";
import { deleteZone } from "../services/api";
import { useRouter } from "vue-router";
import _ from "lodash";
import useBulkDelete from "./useBulkDelete";

export const useZoneActions = (onDeleteSuccess?: () => void, onDeleteError?: (error?: AxiosError) => void) => {
    const { handleError } = useErrorHandler();
    const { onBulkDelete } = useBulkDelete();
    const router = useRouter();

    const onNavigate = (zone: DNSZone) => {
        router.push({ name: "ZoneDetails", params: { name: zone.name } });
    };

    const onDelete = async (zones: DNSZone | DNSZone[]) => {
        const isArray = _.isArray(zones);

        if (isArray && zones.length > 1) {
            const { failed } = await onBulkDelete<DNSZone>(zones, (z: DNSZone) => deleteZone(z.name), "zone", "name");

            if (!_.isEmpty(failed)) {
                return onDeleteError?.();
            }

            return onDeleteSuccess?.();
        }

        const zone = isArray ? zones[0] : zones;

        deleteZone(zone.name)
            .then(onDeleteSuccess)
            .catch((error: AxiosError) => {
                if (error.response?.status !== HttpStatusCode.NotFound) {
                    handleError(error);
                }

                onDeleteError?.(error);
            });
    };

    return {
        onDelete,
        onNavigate,
    };
};
