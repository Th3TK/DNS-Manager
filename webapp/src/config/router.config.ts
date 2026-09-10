import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/LoginView.vue";
import DashboardView from "../views/DashboardView.vue";
import TrashView from "../views/TrashView.vue";
import ZoneListView from "../views/ZoneListView.vue";
import ZoneDetailView from "../views/ZoneDetailView.vue";
import ChangeHistoryView from "../views/ChangeHistoryView.vue";
import UserManagementView from "../views/UserManagementView.vue";
import { LayoutBoard, World, History, Trash, Users, ListDetails } from "@vicons/tabler";
import ChangeHistoryEntryView from "../views/ChangeHistoryEntryView.vue";
import TrashEntryView from "../views/TrashEntryView.vue";
import RecordDetailView from "../views/RecordDetailView.vue";
import { useAuthenticationStore } from "../stores/useAuthenticationStore.ts";
import { pinia } from "./pinia.config.ts";
import RecordListView from "../views/RecordListView.vue";

export const routes = [
    {
        name: "Login",
        path: "/login",
        component: LoginView,
        meta: {
            hide: true,
            public: true,
        },
    },
    {
        name: "Dashboard",
        path: "/",
        component: DashboardView,
        meta: {
            icon: LayoutBoard,
        },
    },
    {
        name: "Zones",
        path: "/zones",
        component: ZoneListView,
        meta: {
            icon: World,
        },
    },
    {
        name: "ZoneDetails",
        path: "/zones/:name",
        component: ZoneDetailView,
        meta: {
            hide: true,
        },
    },
    {
        name: "Records",
        path: "/records",
        component: RecordListView,
        meta: {
            icon: ListDetails,
        },
    },
    {
        name: "RecordDetails",
        path: "/zones/:name/record/:record_name/:record_type",
        component: RecordDetailView,
        meta: {
            hide: true,
        },
    },
    {
        name: "Trash",
        path: "/trash",
        component: TrashView,
        meta: {
            icon: Trash,
        },
    },
    {
        name: "TrashEntryDetails",
        path: "/trash/:uuid",
        component: TrashEntryView,
        meta: {
            icon: Trash,
            hide: true,
        },
    },
    {
        name: "History",
        path: "/history",
        component: ChangeHistoryView,
        meta: {
            icon: History,
        },
    },
    {
        name: "HistoryEntryDetails",
        path: "/history/:uuid",
        component: ChangeHistoryEntryView,
        meta: {
            icon: History,
            hide: true,
        },
    },
    {
        name: "Users",
        path: "/users",
        component: UserManagementView,
        meta: {
            icon: Users,
            adminRequired: true,
        },
    },
];

const authentication = useAuthenticationStore(pinia);

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach(async (to, from) => {
    if (to.meta.public) return;

    await authentication.refresh();

    // send unauthenticated sessions straight to login page
    if (!authentication.user) return { name: "Login" };

    // send authenticated users to dashboard
    if (to.name === "Login") return { name: "Dashboard" };

    // forbid not authorized users to view admin only routes
    if (to.meta.adminRequired && !authentication.user.is_admin) return { name: "Dashboard" };
});

export default router;
