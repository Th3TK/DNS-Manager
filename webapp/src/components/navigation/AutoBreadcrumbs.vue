<script setup lang="ts">
import _ from "lodash";
import { NBreadcrumb, NBreadcrumbItem, NCard, NText } from "naive-ui";
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import type { RouteBreadcrumb } from "../../types/app.types";

const route = useRoute();
const router = useRouter();

// const breadcrumbs = computed(() => {
//     const segments = route.path.split("/").filter(Boolean);
//     const routes = router.getRoutes();

//     return segments.map((segment, index) => {
//         const path = "/" + segments.slice(0, index + 1).join("/");

//         const matchedRoute = routes.find((record) => {
//             const pattern = record.path.replace(/:[^/]+/g, "[^/]+").replace(/\//g, "\\/");

//             return new RegExp(`^${pattern}$`).test(path);
//         });

//         const isDynamic = matchedRoute?.path.split("/").some((part) => part.startsWith(":"));

//         return {
//             path,
//             label: isDynamic ? segment : (matchedRoute?.name?.toString() ?? formatSegment(segment)),
//             clickable: !!matchedRoute,
//         };
//     });
// });

const breadcrumbs = computed(() => {
    if (!_.isArray(route.meta?.breadcrumbs)) return [];

    return route.meta.breadcrumbs.map((breadcrumb: RouteBreadcrumb, i) => {
        const isClickable = router.getRoutes().find((record) => record.path === breadcrumb.to);
        const path = breadcrumb.to
            .split("/")
            .map((part) => (part.startsWith(":") ? route.params[part.slice(1)] : part))
            .join("/");

        const isDynamicLabel = breadcrumb.title.startsWith(":");
        const label = isDynamicLabel ? route.params[breadcrumb.title.slice(1)] : breadcrumb.title;

        return { path, label, isClickable };
    });
});
</script>

<template>
    <NCard
        v-if="breadcrumbs.length"
        content-class="card"
    >
        <NBreadcrumb>
            <NBreadcrumbItem
                v-for="breadcrumb in breadcrumbs"
                :key="breadcrumb.path"
                @click="breadcrumb.isClickable ? router.push(breadcrumb.path) : () => {}"
            >
                <NText>
                    {{ breadcrumb.label }}
                </NText>
            </NBreadcrumbItem>
        </NBreadcrumb>
    </NCard>
</template>

<style scoped>
:deep(.card) {
    padding: var(--spacing-sm) !important;
}
.breadcrumb-link {
    display: flex;
    align-items: center;
    width: 100%;
    height: 100%;
}
</style>
