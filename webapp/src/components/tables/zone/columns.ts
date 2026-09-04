import { h } from "vue";
import TextField from "../../data-table/fields/TextField.vue";
import type { DNSZone } from "../../../types/api.types.ts";
import type { DataTableColumns } from "naive-ui";
import ActorField from "../../data-table/fields/ActorField.vue";
import ZoneControls from "../../controls/ZoneControls.vue";

export const getColumns = (refresh: () => void): DataTableColumns<DNSZone> => [
    {
        type: "selection",
    },
    {
        title: "Name",
        key: "name",
        sorter: "default",
        render: (row: DNSZone) =>
            h(TextField, {
                value: row.name,
                copyOption: true,
                monospace: true,
            }),
    },

    {
        title: "Comment",
        key: "comment",
        sorter: "default",
        render: (row: DNSZone) =>
            h(TextField, {
                value: row.comment || "-",
            }),
    },
    {
        title: "Author",
        key: "author",
        sorter: "default",
        render: (row: DNSZone) =>
            h(ActorField, {
                value: row.author,
            }),
    },

    {
        title: "Number of records",
        key: "record_count",
        sorter: "default",
        render: (row: DNSZone) =>
            h(TextField, {
                value: String(row.record_count),
            }),
        width: 180,
    },
    {
        title: "",
        key: "controls",
        render: (row: DNSZone) =>
            h(ZoneControls, {
                zones: row,
                dropdown: true,
                onDeleteError: refresh,
                onDeleteSuccess: refresh,
            }),
        width: 60,
    },
];
