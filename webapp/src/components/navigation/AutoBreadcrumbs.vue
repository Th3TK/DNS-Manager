<script setup lang="ts">
import { NBreadcrumb, NBreadcrumbItem, NCard, NText } from "naive-ui";
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const breadcrumbs = computed(() => {
    const segments = route.path.split("/").filter(Boolean);
    const routes = router.getRoutes();

    return segments.map((segment, index) => {
        const path = "/" + segments.slice(0, index + 1).join("/");

        const matchedRoute = routes.find((record) => {
            const pattern = record.path.replace(/:[^/]+/g, "[^/]+").replace(/\//g, "\\/");

            return new RegExp(`^${pattern}$`).test(path);
        });

        const isDynamic = matchedRoute?.path.split("/").some((part) => part.startsWith(":"));

        return {
            path,
            label: isDynamic ? segment : (matchedRoute?.name?.toString() ?? formatSegment(segment)),
            clickable: !!matchedRoute,
        };
    });
});

function formatSegment(segment: string) {
    return segment.charAt(0).toUpperCase() + segment.slice(1).toLowerCase();
}
</script>

<template>
    <NCard
        content-class="card"
        v-if="breadcrumbs.length"
    >
        <NBreadcrumb>
            <NBreadcrumbItem> <RouterLink to="/"> Dashboard </RouterLink> </NBreadcrumbItem>
            <NBreadcrumbItem
                v-for="breadcrumb in breadcrumbs"
                :key="breadcrumb.path"
                @click="breadcrumb.clickable ? router.push(breadcrumb.path) : () => {}"
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
