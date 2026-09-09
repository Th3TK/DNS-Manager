import type { DataTableColumns } from "naive-ui";
import type { APIRecordStatus, DisplayedRecordStatus, DNSRecordExtended } from "../../../types/api.types";
import BadgeField from "../../data-table/fields/BadgeField.vue";
import _ from "lodash";
import { h } from "vue";
import RecordControls from "../../controls/RecordControls.vue";
import StatusField from "../../data-table/fields/StatusField.vue";
import TextField from "../../data-table/fields/TextField.vue";
import DateField from "../../data-table/fields/DateField.vue";

export const getColumns = (refresh: () => void): DataTableColumns<DNSRecordExtended> => [
    {
        type: "selection",
        multiple: true,
    },
    {
        title: "Name",
        key: "name",
        sorter: "default",
        render: (row: DNSRecordExtended) =>
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
        render: (row: DNSRecordExtended) =>
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
        render: (row: DNSRecordExtended) =>
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
        render: (row: DNSRecordExtended) =>
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
    {
        title: "Status",
        key: "displayed_status",
        sorter: "default",
        render: (row: DNSRecordExtended) =>
            h(StatusField, {
                displayed_status: row.displayed_status,
                api_status: row.api_status,
            }),
        width: 220,
    },
    {
        title: "Last status check",
        key: "status_timestamp",
        sorter: "default",
        render: (row: DNSRecordExtended) =>
            row.status_timestamp
                ? h(DateField, {
                      value: row.status_timestamp,
                  })
                : "-",
        width: 180,
    },

    {
        title: "",
        key: "controls",
        render: (row: DNSRecordExtended) =>
            h(RecordControls, {
                zoneName: row.zone_name,
                records: row,
                type: "dropdown",
                onDeleteError: refresh,
                onDeleteSuccess: refresh,
                onEditSuccess: refresh,
            }),
        width: 60,
    },
];

export const getColumnsForAllRecordsTable = (): DataTableColumns<DNSRecordExtended> => [
    {
        title: "Zone",
        key: "zone_name",
        sorter: "default",
        render: (row: DNSRecordExtended) =>
            h(TextField, {
                value: row.zone_name,
                monospace: true,
                copyOption: true,
            }),
    },
    {
        title: "Name",
        key: "name",
        sorter: "default",
        render: (row: DNSRecordExtended) =>
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
        render: (row: DNSRecordExtended) =>
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
        render: (row: DNSRecordExtended) =>
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
        render: (row: DNSRecordExtended) =>
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
    {
        title: "Status",
        key: "displayed_status",
        sorter: "default",
        render: (row: DNSRecordExtended) =>
            h(StatusField, {
                displayed_status: row.displayed_status,
                api_status: row.api_status,
            }),
        width: 220,
    },
    {
        title: "Last status check",
        key: "status_timestamp",
        sorter: "default",
        render: (row: DNSRecordExtended) =>
            row.status_timestamp
                ? h(DateField, {
                      value: row.status_timestamp,
                  })
                : "-",
        width: 180,
    },
];
