import { NFlex, NIcon, type DataTableColumns } from "naive-ui";
import type { NameSearchDNSRecord } from "../../../types/api.types";
import { h } from "vue";
import BadgeField from "../../data-table/fields/BadgeField.vue";
import TextField from "../../data-table/fields/TextField.vue";
import _ from "lodash";
import { naturalCompare } from "../../../utils/sorters.ts";

export const columns: DataTableColumns<NameSearchDNSRecord> = [
    {
        title: "Name",
        key: "name",
        sorter: (a, b) => naturalCompare(a.name ?? "", b.name ?? ""),
        render: (row: NameSearchDNSRecord) =>
            h(TextField, {
                value: row.name,
                monospace: true,
            }),
    },

    {
        title: "Type",
        key: "type",
        sorter: "default",
        render: (row: NameSearchDNSRecord) =>
            h(BadgeField, {
                value: row.type,
                variants: {
                    A: { type: "primary" },
                    AAAA: { type: "primary" },
                    CNAME: { type: "error" },
                    TXT: { type: "info" },
                    MX: { type: "warning" },
                    SRV: { type: "warning" },
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
        sorter: (a, b) => naturalCompare([a.content].flat().join(","), [b.content].flat().join(",")),
        render: (row: NameSearchDNSRecord) =>
            h(TextField, {
                value: _.isArray(row.content) ? row.content.join("\n") : row.content,
                monospace: true,
            }),
    },

    {
        title: "Zone",
        key: "zone_name",
        sorter: (a, b) => naturalCompare(a.zone_name, b.zone_name),
        render: (row: NameSearchDNSRecord) =>
            h(TextField, {
                value: row.zone_name,
                monospace: true,
            }),
    },
    {
        title: "Origin",
        key: "origin",
        sorter: "default",
        render: (row: NameSearchDNSRecord) =>
            h(BadgeField, {
                value: row.origin,
                label: _.capitalize(row.origin),
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

        width: 200,
    },
    {
        title: "Location",
        key: "location",
        sorter: "default",
        render: (row: NameSearchDNSRecord) =>
            h(BadgeField, {
                value: row.location,
                label: _.capitalize(row.location),
                variants: {
                    active: {
                        type: "success",
                    },
                    trash: {
                        type: "default",
                    },
                },
                default: {
                    bordered: false,
                    round: true,
                },
            }),

        width: 200,
    },
];
