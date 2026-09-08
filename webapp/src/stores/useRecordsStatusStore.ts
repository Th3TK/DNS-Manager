import { defineStore } from "pinia";
import { useWebSocket } from "../composables/useWebSocket";
import { ref, watch } from "vue";
import type { APIRecordStatus, APIRecordStatusCheckData, DisplayedRecordStatus, RecordStatusCheckData } from "../types/api.types";
import _ from "lodash";

export const useRecordsStatusStore = defineStore("records-status", () => {
    const { lastMessage, connected, connect } = useWebSocket<APIRecordStatusCheckData>("/status-check");

    const data = ref<RecordStatusCheckData | null>(null);

    const generateDisplayStatus = (responseStatus: APIRecordStatus | null): DisplayedRecordStatus => {
        if (_.isNull(responseStatus)) return "DISABLED";
        if (responseStatus.resolution === "NO_RESOLUTION") return "ERROR";
        if (responseStatus.resolution === "MISMATCH" || responseStatus.reachability === "UNREACHABLE") return "WARNING";
        return "OK";
    };

    watch(data, () => console.log(data.value));

    watch([connected, lastMessage], () => {
        console.log(connected.value, lastMessage.value);

        if (!connected.value) {
            return;
        }

        if (_.isNull(lastMessage.value)) {
            data.value = lastMessage.value;
            return;
        }

        const counts: Record<DisplayedRecordStatus, number> = {
            DISABLED: 0,
            ERROR: 0,
            WARNING: 0,
            OK: 0,
        };

        _.forEach(lastMessage.value.statuses, (names) => {
            _.forEach(names, (types) => {
                _.forEach(types, (status) => {
                    const displayStatus = generateDisplayStatus(status);
                    counts[displayStatus]++;
                });
            });
        });

        data.value = {
            counts: counts,
            statuses: lastMessage.value.statuses,
            timestamp: new Date(lastMessage.value.timestamp),
            next_check: new Date(lastMessage.value.next_check),
        };
    });

    return { data, generateDisplayStatus, connect };
});
