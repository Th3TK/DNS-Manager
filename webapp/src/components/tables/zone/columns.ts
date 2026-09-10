import { h } from "vue";
import TextField from "../../data-table/fields/TextField.vue";
import type { DNSZone } from "../../../types/api.types.ts";
import type { DataTableColumns } from "naive-ui";
import ActorField from "../../data-table/fields/ActorField.vue";
import ZoneControls from "../../controls/ZoneControls.vue";
import { naturalCompare, compareNumbers } from "../../../utils/sorters.ts";

export const getColumns = (refresh: () => void): DataTableColumns<DNSZone> => [
    {
        type: "selection",
        options: ["all", "none"],
    },
    {
        title: "Name",
        key: "name",
        sorter: (a, b) => naturalCompare(a.name, b.name),
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
        sorter: (a, b) => naturalCompare(a.comment ?? "", b.comment ?? ""),
        render: (row: DNSZone) =>
            h(TextField, {
                value: row.comment || "-",
            }),
    },
    {
        title: "Author",
        key: "author",
        sorter: (a, b) => naturalCompare(a.author ?? "", b.author ?? ""),
        render: (row: DNSZone) =>
            h(ActorField, {
                value: row.author,
            }),
    },

    {
        title: "Number of records",
        key: "record_count",
        sorter: (a, b) => compareNumbers(a.record_count ?? 0, b.record_count ?? 0),
        render: (row: DNSZone) =>
            h(TextField, {
                value: row.record_count === null ? "-" : String(row.record_count),
            }),
    },
    {
        title: "",
        key: "controls",
        render: (row: DNSZone) =>
            h(ZoneControls, {
                zones: row,
                type: "dropdown",
                dropdown: true,
                onDeleteError: refresh,
                onDeleteSuccess: refresh,
            }),
        width: 60,
    },
];
