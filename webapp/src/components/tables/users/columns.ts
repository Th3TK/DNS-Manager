import type { DataTableColumns } from "naive-ui";
import type { User } from "../../../types/api.types";
import TextField from "../../data-table/fields/TextField.vue";
import { h } from "vue";
import BooleanField from "../../data-table/fields/BooleanField.vue";
import BadgeField from "../../data-table/fields/BadgeField.vue";
import UserControls from "../../controls/UserControls.vue";

export const getColumns = (refresh: () => void): DataTableColumns<User> => [
    {
        type: "selection",
    },
    {
        title: "Username",
        key: "username",
        sorter: "default",
        render: (row: User) =>
            h(TextField, {
                value: row.username,
                copyOption: true,
                monospace: true,
            }),
    },
    {
        title: "Full name",
        key: "full_name",
        sorter: "default",
        render: (row: User) =>
            h(TextField, {
                value: row.full_name,
            }),
    },
    {
        title: "Role",
        key: "is_admin",
        sorter: "default",
        render: (row: User) =>
            h(BadgeField, {
                value: String(row.is_admin),
                label: row.is_admin ? "Administrator" : "Viewer",
                variants: {
                    true: { type: "error" },
                    false: { type: "info" },
                },
                default: {
                    bordered: false,
                    round: true,
                    size: "small",
                },
            }),
    },
    {
        title: "Disabled",
        key: "disabled",
        sorter: "default",
        render: (row: User) =>
            h(BooleanField, {
                value: row.disabled,
            }),
    },
    {
        title: "",
        key: "controls",
        render: (row: User) =>
            h(UserControls, {
                users: row,
                type: "dropdown",
                onDeleteError: refresh,
                onDeleteSuccess: refresh,
                onEditSuccess: refresh,
            }),
        width: 60,
    },
];
