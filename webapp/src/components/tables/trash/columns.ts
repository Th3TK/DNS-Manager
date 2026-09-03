import type { DataTableColumns } from "naive-ui";
import type { TrashEntry } from "../../../types/api.types";
import { h } from "vue";
import BadgeField from "../../data-table/fields/BadgeField.vue";
import ActorField from "../../data-table/fields/ActorField.vue";
import DNSObjectField from "../../data-table/fields/DNSObjectField.vue";
import TimeToLiveField from "../../data-table/fields/TimeToLiveField.vue";
import TrashEntryControls from "../../data-table/fields/TrashEntryControls.vue";

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
        width: 200,
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
        width: 300,
        sorter: "default",
    },
    {
        title: "Time to live",
        key: "deletion_timestamp",
        render: (row: TrashEntry) =>
            h(TimeToLiveField, {
                deletionTimestamp: new Date(row.deletion_timestamp),
            }),
        width: 200,
        sorter: "default",
    },
    {
        title: "Controls",
        key: "controls",
        render: (row: TrashEntry) =>
            h(TrashEntryControls, {
                entry: row,
                refresh,
            }),
        width: 120,
    },
];
