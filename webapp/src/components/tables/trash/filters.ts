import _ from "lodash";
import type { TrashEntry, User } from "../../../types/api.types";
import type { FilterConfig } from "../../../types/table.types";

export const getFilters = (users: User[]): FilterConfig<TrashEntry> => ({
    actor: {
        type: "options",
        options: _.map(users, (user: User) => ({
            label: user.full_name || user.username,
            value: user.username,
        })),
    },
    object_type: {
        type: "options",
        options: [
            { label: "Zone", value: "zone" },
            { label: "Record", value: "record" },
        ],
    },
});
