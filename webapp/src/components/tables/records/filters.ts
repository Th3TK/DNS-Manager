import _ from "lodash";
import type { DNSRecord, User } from "../../../types/api.types";
import type { FilterConfig } from "../../../types/table.types";

export const getFilters = (users: User[]): FilterConfig<DNSRecord> => ({
    zone_name: { type: "freetext" },
    name: { type: "freetext" },
    content: { type: "freetext" },
    comment: { type: "freetext" },
    type: {
        type: "options",
        options: [
            { label: "A", value: "A" },
            { label: "AAAA", value: "AAAA" },
            { label: "CNAME", value: "CNAME" },
            { label: "TXT", value: "TXT" },
            { label: "MX", value: "MX" },
            { label: "SRV", value: "SRV" },
            { label: "SOA", value: "SOA" },
            { label: "NS", value: "NS" },
        ],
    },
    author: {
        type: "options",
        options: _.map(users, (user: User) => ({ label: user.full_name || user.username, value: user.username })),
    },
});
