import _ from "lodash";
import type { ChangeHistoryEntry, User } from "../../../types/api.types";
import type { FilterConfig } from "../../../types/table.types";

export const getFilters = (users: User[]): FilterConfig<ChangeHistoryEntry> => ({
    action: {
        type: "options",
        options: [
            { label: "Created", value: "created" },
            { label: "Changed", value: "changed" },
            { label: "Deleted", value: "deleted" },
            { label: "Restored", value: "restored" },
            { label: "Permanently Deleted", value: "permanently_deleted" },
        ],
    },

    actor: {
        type: "options",
        options: _.map(users, (user: User) => ({ label: user.full_name || user.username, value: user.username })),
    },

    affected_object_name: {
        type: "freetext",
    },
    affected_object_type: {
        type: "options",
        options: [
            { label: "Record", value: "record" },
            { label: "Zone", value: "zone" },
        ],
    },
    action_timestamp: {
        type: "datetime",
    },
});
