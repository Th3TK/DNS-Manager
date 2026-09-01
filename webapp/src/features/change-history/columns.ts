import type { DataTableColumns } from "naive-ui";
import type { ChangeHistoryEntry } from "../../types/api.types";
import { h } from "vue";
import TextField from "../../components/data-table/fields/TextField.vue";
import DateField from "../../components/data-table/fields/DateField.vue";
import BadgeField from "../../components/data-table/fields/BadgeField.vue";
import ActorField from "../../components/data-table/fields/ActorField.vue";

export const columns: DataTableColumns<ChangeHistoryEntry> = [
    {
        title: "Timestamp",
        key: "action_timestamp",
        render: (row: ChangeHistoryEntry) =>
            h(DateField, {
                value: new Date(row.action_timestamp),
            }),
    },
    {
        title: "Actor",
        key: "actor",
        render: (row: ChangeHistoryEntry) =>
            h(ActorField, {
                value: row.actor,
            }),
    },
    {
        title: "Action",
        key: "action",
        render: (row: ChangeHistoryEntry) =>
            h(BadgeField, {
                value: row.action.replace("_", " ").toUpperCase(),
                variants: {
                    CREATED: {
                        type: "success",
                    },
                    CHANGED: {
                        type: "info",
                    },
                    RESTORED: {
                        type: "success",
                    },
                    DELETED: {
                        type: "warning",
                    },
                    "PERMANENTLY DELETED": {
                        type: "error",
                    },
                },
                default: {
                    bordered: false,
                    round: true,
                    size: "small",
                },
            }),
    },
    {
        title: "Object type",
        key: "affected_object_type",
        render: (row: ChangeHistoryEntry) =>
            h(BadgeField, {
                value: row.affected_object_type.toUpperCase(),
                default: {
                    type: "default",
                    bordered: false,
                    round: true,
                    size: "small",
                },
            }),
    },
    {
        title: "Object name",
        key: "affected_object_name",
        render: (row: ChangeHistoryEntry) =>
            h(TextField, {
                value: row.affected_object_name,
                copyOption: true,
            }),
    },
];
