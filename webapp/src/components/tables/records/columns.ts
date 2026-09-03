import type { DataTableColumns } from "naive-ui";
import type { DNSRecord } from "../../../types/api.types";
import BadgeField from "../../data-table/fields/BadgeField.vue";
import TextField from "../../data-table/fields/TextField.vue";
import _ from "lodash";
import { h } from "vue";

export const columns: DataTableColumns<DNSRecord> = [
    {
        type: "selection",
        multiple: true,
    },
    {
        title: "Name",
        key: "name",
        sorter: "default",
        render: (row: DNSRecord) =>
            h(TextField, {
                value: row.name,
                monospace: true,
                copyOption: true,
            }),
    },

    {
        title: "Type",
        key: "type",
        sorter: "default",
        render: (row: DNSRecord) =>
            h(BadgeField, {
                value: row.type,
                variants: {
                    A: { type: "primary" },
                    AAAA: { type: "primary" },
                    CNAME: { type: "error" },
                    TXT: { type: "info" },
                    MX: { type: "success" },
                    SRV: { type: "success" },
                },
                default: {
                    bordered: false,
                    type: "default",
                },
            }),

        width: 100,
    },

    {
        title: "Content",
        key: "content",
        sorter: "default",
        render: (row: DNSRecord) =>
            h(TextField, {
                value: _.isArray(row.content) ? row.content.join("\n") : row.content,
                monospace: true,
                copyOption: true,
            }),
    },

    {
        title: "Origin",
        key: "origin",
        sorter: "default",
        render: (row: DNSRecord) =>
            h(BadgeField, {
                value: row.origin,
                variants: {
                    external: {
                        type: "default",
                    },
                    manual: {
                        type: "success",
                    },
                    "automatic => traefik": {
                        type: "info",
                    },
                },
                default: {
                    bordered: false,
                    round: true,
                },
            }),

        width: 150,
    },
    {
        title: "TTL",
        key: "ttl",
        sorter: "default",
        width: 100,
    },
];
