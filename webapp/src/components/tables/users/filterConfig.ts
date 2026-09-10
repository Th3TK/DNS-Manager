import type { User } from "../../../types/api.types";
import type { FilterConfig } from "../../../types/table.types";

export const filters: FilterConfig<User> = {
    username: {
        type: "freetext",
    },
    full_name: {
        type: "freetext",
    },
    is_admin: {
        type: "options",
        options: [
            { label: "Administrator", value: "true" },
            { label: "Viewer", value: "false" },
        ],
    },
    disabled: {
        type: "options",
        options: [
            { label: "True", value: 1 },
            { label: "False", value: 0 },
        ],
    },
};
