import { HttpStatusCode, type AxiosError } from "axios";
import type { DNSRecord } from "../types/api.types";
import { useErrorHandler } from "./useErrorHandler";
import { ref, type Ref } from "vue";
import { deleteRecord } from "../services/api";
import { useRouter } from "vue-router";
import _ from "lodash";
import useBulkDelete from "./useBulkDelete";

export const useRecordActions = (onDeleteSuccess?: () => void, onDeleteError?: (error?: AxiosError) => void) => {
    const { handleError } = useErrorHandler();
    const { onBulkDelete } = useBulkDelete();
    const router = useRouter();

    const onNavigate = (record: DNSRecord) => {
        router.push({
            name: "RecordDetails",
            params: { name: record.zone_name, record_name: record.name, record_type: record.type },
        });
    };

    const onDelete = async (records: DNSRecord | DNSRecord[]) => {
        const isArray = _.isArray(records);

        if (isArray && records.length > 1) {
            const { failed } = await onBulkDelete<DNSRecord>(
                records,
                (r: DNSRecord) => deleteRecord(r.zone_name, r.name, r.type),
                "record",
                "name",
            );

            if (!_.isEmpty(failed)) {
                return onDeleteError?.();
            }

            return onDeleteSuccess?.();
        }

        const record = isArray ? records[0] : records;

        deleteRecord(record.zone_name, record.name, record.type)
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
