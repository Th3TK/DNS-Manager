import _ from "lodash";
import type { ChangeHistoryEntry, User } from "../../../types/api.types";
import type { FilterConfig } from "../../../types/table.types";

export const getFilters = (users: User[]): FilterConfig<ChangeHistoryEntry> => ({
    action: {
        type: "options",
        options: [
            { label: "Created", value: "created" },
            { label: "Changed", value: "Changed" },
            { label: "Deleted", value: "Deleted" },
            { label: "Restored", value: "Restored" },
            { label: "Permanently Deleted", value: "Permanently Deleted" },
        ],
    },

    actor: {
        type: "options",
        options: _.map(users, (user: User) => ({ label: user.full_name || user.username, value: user.username })),
    },

    affected_object_name: {
        type: "freetext",
    },
});
