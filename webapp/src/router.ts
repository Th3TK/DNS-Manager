import { createRouter, createWebHistory } from "vue-router";
import LoginView from "./views/LoginView.vue";
import DashboardView from "./views/DashboardView.vue";
import TrashView from "./views/TrashView.vue";
import ZoneListView from "./views/ZoneListView.vue";
import ZoneDetailView from "./views/ZoneDetailView.vue";
import ChangeHistoryView from "./views/ChangeHistoryView.vue";
import UserManagementView from "./views/UserManagementView.vue";
import { getAuthenticatedUser } from "./services/api.ts";
import { LayoutBoard, World, History, Trash, Users } from "@vicons/tabler";

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
        name: "Trash",
        path: "/trash",
        component: TrashView,
        meta: {
            icon: Trash,
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
        name: "Users",
        path: "/users",
        component: UserManagementView,
        meta: {
            icon: Users,
            adminRequired: true,
        },
    },
];

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach(async (to, from) => {
    if (to.meta.public) return;

    let user = await getAuthenticatedUser();

    // send unauthenticated sessions straight to login page
    if (!user) return to.name !== "Login";

    // send authenticated users to dashboard
    if (to.name === "Login") return { name: "Dashboard" };

    // forbid not authorized users to view admin only routes
    if (to.meta.adminRequired && !user.is_admin) return { name: "Dashboard" };
});

export default router;
