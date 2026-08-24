import { createRouter, createWebHistory } from "vue-router";
import LoginView from "./views/LoginView.vue";
import DashboardView from "./views/DashboardView.vue";
import TrashView from "./views/TrashView.vue";
import ZoneListView from "./views/ZoneListView.vue";
import ZoneDetailView from "./views/ZoneDetailView.vue";
import ChangeHistoryView from "./views/ChangeHistoryView.vue";
import UserManagementView from "./views/UserManagementView.vue";

const routes = [
    { path: "/", component: DashboardView },
    { path: "/login", component: LoginView },
    { path: "/zones", component: ZoneListView },
    { path: "/zones/:name", component: ZoneDetailView },
    { path: "/history", component: ChangeHistoryView },
    { path: "/trash", component: TrashView },
    { path: "/users", component: UserManagementView },
];

export const router = createRouter({
    history: createWebHistory(),
    routes,
});
