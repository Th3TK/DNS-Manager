import _ from "lodash";
import type { DNSRecordExtended, User } from "../../../types/api.types";
import type { FilterConfig } from "../../../types/table.types";

export const getFilters = (users: User[]): FilterConfig<DNSRecordExtended> => ({
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
    displayed_status: {
        type: "options",
        options: [
            { label: "Ok", value: "OK" },
            { label: "Warning", value: "WARNING" },
            { label: "Error", value: "ERROR" },
            { label: "Disabled", value: "Disabled" },
        ],
    },
    origin: {
        type: "options",
        options: [
            { label: "Manual", value: "manual" },
            { label: "Automatic", value: "automatic => traefik" },
            { label: "External", value: "external" },
        ],
    },
    ttl: {
        type: "range",
        min: 0,
        max: 2_147_483_647,
    },
});
