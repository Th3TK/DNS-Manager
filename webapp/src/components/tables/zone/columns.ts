import { h } from "vue";
import TextField from "../../data-table/fields/TextField.vue";
import type { DNSZone } from "../../../types/api.types.ts";
import BadgeField from "../../data-table/fields/BadgeField.vue";
import type { DataTableColumns } from "naive-ui";

export const columns: DataTableColumns<DNSZone> = [
    {
        type: "selection",
        multiple: false,
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
            h(TextField, {
                value: row.author ?? "-",
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
];
