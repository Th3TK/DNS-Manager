import type { DataTableColumns } from "naive-ui";
import type { ChangeHistoryEntry } from "../../../types/api.types";
import { h } from "vue";
import TextField from "../../data-table/fields/TextField.vue";
import DateField from "../../data-table/fields/DateField.vue";
import BadgeField from "../../data-table/fields/BadgeField.vue";
import ActorField from "../../data-table/fields/ActorField.vue";
import ActionTypeTag from "../../display/ActionTypeTag.vue";

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
            h(ActionTypeTag, {
                value: row.action,
                size: "small",
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
                monospace: true,
            }),
    },
];
