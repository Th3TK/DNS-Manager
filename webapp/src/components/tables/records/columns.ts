import type { DataTableColumn, DataTableColumns } from "naive-ui";
import type { DNSRecordExtended } from "../../../types/api.types";
import BadgeField from "../../data-table/fields/BadgeField.vue";
import _ from "lodash";
import { h } from "vue";
import RecordControls from "../../controls/RecordControls.vue";
import StatusField from "../../data-table/fields/StatusField.vue";
import TextField from "../../data-table/fields/TextField.vue";
import { naturalCompare, compareNumbers, compareStatus } from "../../../utils/sorters.ts";

/*
TODO

1. Replace the controls column with a more optimized solution.

Each row receives a controls dropdown which has embeded multiple modals for each action (edit, delete).
Should open a centrally controlled modal instead.

2. Tests show that using the "render" field slows down this table tremendously. This starts to get visible when user displays more than 25 entries per page.

*/

export const getColumns = (global: boolean, refresh: () => void): DataTableColumns<DNSRecordExtended> => {
    const columns: (DataTableColumn<DNSRecordExtended> | undefined)[] = [
        global
            ? ({
                  title: "Zone",
                  key: "zone_name",
                  sorter: (a, b) => naturalCompare(a.zone_name, b.zone_name),
                  render: (row: DNSRecordExtended) =>
                      h(TextField, {
                          value: row.zone_name,
                          monospace: true,
                      }),
              } as DataTableColumn<DNSRecordExtended>)
            : ({
                  type: "selection",
                  multiple: true,
                  options: ["all", "none"],
              } as DataTableColumn<DNSRecordExtended>),
        {
            title: "Name",
            key: "name",
            sorter: (a, b) => naturalCompare(a.name, b.name),
            render: (row: DNSRecordExtended) =>
                h(TextField, {
                    value: row.name,
                    monospace: true,
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
            render: (row: DNSRecordExtended) =>
                h(TextField, {
                    value: _.isArray(row.content) ? row.content.join("\n") : row.content,
                    monospace: true,
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

            width: 175,
        },
        {
            title: "TTL",
            key: "ttl",
            sorter: (a, b) => compareNumbers(a.ttl, b.ttl),
            width: 100,
        },
        {
            title: "Status",
            key: "displayed_status",
            sorter: (a, b) => compareStatus(a.displayed_status, b.displayed_status),
            render: (row: DNSRecordExtended) =>
                h(StatusField, {
                    displayed_status: row.displayed_status,
                    api_status: row.api_status,
                }),
            width: 150,
        },

        !global
            ? ({
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
              } as DataTableColumn<DNSRecordExtended>)
            : undefined,
    ];

    return columns.filter((e): e is DataTableColumn<DNSRecordExtended> => e !== undefined);
};
