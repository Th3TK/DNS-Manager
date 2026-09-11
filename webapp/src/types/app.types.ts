import type { Component } from "vue";
import type { RouteMeta, RouteRecordRedirect, RouteRecordSingleView } from "vue-router";

export interface RouteBreadcrumb {
    title: string;
    to: string;
}

export interface RouteMetaCustom extends RouteMeta {
    icon?: Component;
    public?: boolean;
    hide?: boolean;
    adminRequired?: boolean;
    breadcrumbs?: RouteBreadcrumb[];
}

export type Route = (RouteRecordSingleView | RouteRecordRedirect) & {
    meta: RouteMetaCustom;
};
