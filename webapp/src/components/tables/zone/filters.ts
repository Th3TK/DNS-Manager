import { computed } from "vue";
import type { DNSZone, User } from "../../../types/api.types";
import type { FilterConfig } from "../../../types/table.types";
import _ from "lodash";

export const getFilterConfig = (users: User[]): FilterConfig<DNSZone> => ({
    name: {
        type: "freetext",
    },
    author: {
        type: "options",
        options: _.map(users, (user: User) => ({ label: user.full_name || user.username, value: user.username })),
    },
    comment: {
        type: "freetext",
    },
    origin: {
        type: "options",
        options: [
            { label: "External", value: "external" },
            { label: "Manual", value: "manual" },
        ],
    },
});
