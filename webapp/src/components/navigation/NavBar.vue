<script setup lang="ts">
import { NButton, NCard, NFlex, NIcon, NText } from "naive-ui";
import { computed } from "vue";
import { routes } from "../../config/router.config.ts";
import { useRouter } from "vue-router";
import { useAuthenticationStore } from "../../stores/useAuthenticationStore";
import UserControls from "../controls/UserControls.vue";

const authentication = useAuthenticationStore();
const router = useRouter();

const filteredRoutes = computed(() => routes.filter((e) => !e.meta?.hide && (!e.meta.adminRequired || authentication.isAdmin)));

const isRouteActive = (routeName: string | undefined) => router.currentRoute.value.name === routeName;
</script>

<template>
    <NFlex
        class="navbar"
        vertical
    >
        <NCard
            class="app-name"
            :bordered="false"
        >
            <NText
                tag="h2"
                class="title"
            >
            </NText>
        </NCard>

        <NFlex
            class="segment"
            vertical
        >
            <NText
                depth="3"
                class="segment-text"
            >
                Panel Views
            </NText>

            <NFlex
                class="nav-buttons"
                vertical
            >
                <NButton
                    v-for="route in filteredRoutes"
                    :key="route.name"
                    @click="router.push({ name: route.name })"
                    :tertiary="!isRouteActive(route.name)"
                    :secondary="isRouteActive(route.name)"
                    type="primary"
                    class="nav-button"
                >
                    <template #icon>
                        <NIcon v-if="route.meta?.icon">
                            <component :is="route.meta.icon" />
                        </NIcon>
                    </template>
                    <NText class="nav-button-text">
                        {{ route.name }}
                    </NText>
                </NButton>
            </NFlex>
        </NFlex>

        <NFlex
            class="segment user-segment"
            vertical
        >
            <NText
                depth="3"
                class="segment-text"
            >
                Logged in as
            </NText>
            <UserControls
                :users="authentication.user ?? { username: '', full_name: '', disabled: false, is_admin: false }"
                type="current"
            />
        </NFlex>
    </NFlex>
</template>

<style lang="css" scoped>
.navbar {
    display: flex;
    flex-direction: column;
    height: 100%;
    box-sizing: border-box;
}

.app-name :deep(.n-card-content) {
    padding-top: var(--spacing-md);
    padding-bottom: var(--spacing-md);
    display: flex !important;
    align-items: center;
}

.title {
    margin: 0 !important;
}

.segment {
    padding: var(--spacing-md) 0;
    border-top: 1px solid var(--n-border-color);
}

.segment-text {
    padding: 0 var(--spacing-md);
}

.nav-buttons {
    gap: 0 !important;
}

.nav-button {
    justify-content: flex-start;
    padding: var(--spacing-lg);
    border-color: transparent;
}

.nav-button:not(.n-button--secondary) {
    background-color: transparent;

    &:not(:hover) {
        color: white;
    }
}

.nav-button-text {
    padding-left: var(--spacing-sm);
    color: inherit;
}

.user-segment {
    margin-top: auto;
    min-width: 0;
    width: 100%;
    display: flex;

    box-sizing: border-box;
}
</style>
