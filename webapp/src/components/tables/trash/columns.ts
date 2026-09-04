import type { DataTableColumns } from "naive-ui";
import type { TrashEntry } from "../../../types/api.types";
import { h } from "vue";
import BadgeField from "../../data-table/fields/BadgeField.vue";
import ActorField from "../../data-table/fields/ActorField.vue";
import DNSObjectField from "../../data-table/fields/DNSObjectField.vue";
import TimeToLiveField from "../../data-table/fields/TimeToLiveField.vue";
import TrashControls from "../../controls/TrashControls.vue";

export const getColumns = (refresh?: () => void): DataTableColumns<TrashEntry> => [
    {
        type: "selection",
    },
    {
        title: "Object type",
        key: "object_type",
        render: (row: TrashEntry) =>
            h(BadgeField, {
                value: row.object_type.toUpperCase(),
                default: {
                    type: "default",
                    bordered: false,
                    round: true,
                    size: "small",
                },
            }),
        width: 150,
        sorter: "default",
    },
    {
        title: "Object",
        key: "object_data",
        render: (row: TrashEntry) =>
            h(DNSObjectField, {
                data: row.object_data,
                type: row.object_type,
            }),
    },
    {
        title: "Deleted by",
        key: "actor",
        render: (row: TrashEntry) =>
            h(ActorField, {
                value: row.actor,
            }),
        sorter: "default",
    },
    {
        title: "Permanent deletion",
        key: "deletion_timestamp",
        render: (row: TrashEntry) =>
            h(TimeToLiveField, {
                deletionTimestamp: new Date(row.deletion_timestamp),
            }),
        sorter: "default",
    },
    {
        title: "",
        key: "controls",
        render: (row: TrashEntry) =>
            h(TrashControls, {
                entry: row,
                onDeleteError: refresh,
                onDeleteSuccess: refresh,
                onRestoreError: refresh,
                onRestoreSuccess: refresh,
                dropdown: true,
            }),
        width: 60,
    },
];
