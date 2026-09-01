import type { DataTableColumns } from "naive-ui";
import type { TrashEntry } from "../../types/api.types";
import { h } from "vue";
import DateField from "../../components/data-table/fields/DateField.vue";
import BadgeField from "../../components/data-table/fields/BadgeField.vue";
import ActorField from "../../components/data-table/fields/ActorField.vue";
import DNSObjectField from "../../components/data-table/fields/DNSObjectField.vue";

export const columns: DataTableColumns<TrashEntry> = [
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
    },
    {
        title: "Object",
        key: "object_data",
        render: (row: TrashEntry) =>
            // @ts-expect-error
            h(DNSObjectField, {
                data: row.object_data,
                type: row.object_type,
            }),
    },
    {
        title: "Deletion timestamp",
        key: "deletion_timestamp",
        render: (row: TrashEntry) =>
            h(DateField, {
                value: new Date(row.deletion_timestamp),
            }),
    },
    {
        title: "Deleted by",
        key: "actor",
        render: (row: TrashEntry) =>
            h(ActorField, {
                value: row.actor,
            }),
    },
];
