<script setup lang="ts">
import { NButton, NCard, NFlex, NIcon, NText } from "naive-ui";
import { computed, watch } from "vue";
import { routes } from "../../router";
import { useRouter } from "vue-router";
import { User as IconUser } from "@vicons/tabler";
import useFetch from "../../composables/useFetch";
import { type User } from "../../types/api.types";
import { useErrorHandler } from "../../composables/useErrorHandler";

const { handleError } = useErrorHandler();

const { data: user, error, loading } = useFetch<User>("/users/me");

watch(error, (err) => {
    if (err) handleError(err);
});

const router = useRouter();

const filteredRoutes = computed(() => routes.filter((e) => !e.meta?.hide));

const isRouteActive = (routeName: string) => router.currentRoute.value.name === routeName;
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
            <NText tag="h2">DNS Manager</NText>
        </NCard>

        <NFlex
            class="segment"
            vertical
        >
            <NText
                depth="3"
                class="segment-text"
            >
                Views
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
            class="segment user"
            vertical
        >
            <NText
                depth="3"
                class="segment-text"
            >
                Logged in as
            </NText>
            <NFlex class="user-card">
                <NIcon size="24">
                    <IconUser />
                </NIcon>
                <NFlex
                    class="user-details"
                    vertical
                >
                    <NText
                        class="full-name"
                        ellipsis
                    >
                        {{ user?.full_name || `${user?.username}` }}
                    </NText>
                    <NText
                        class="username"
                        depth="3"
                        ellipsis
                        v-if="user?.full_name"
                    >
                        {{ `${user?.username}` }}
                    </NText>
                </NFlex>
            </NFlex>
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
    padding-top: 0;
    padding-bottom: 0;
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

.user {
    margin-top: auto;
    min-width: 0;
    width: 100%;
    display: flex;

    box-sizing: border-box;
}

.user-card {
    display: flex;
    padding: var(--spacing-sm) var(--spacing-xs) var(--spacing-sm) var(--spacing-md);
    gap: var(--spacing-sm) !important;
    align-items: center;
    min-width: 0;
    width: 100%;
    box-sizing: border-box;
}

.user-details {
    min-width: 0;
    flex: 1;
    gap: 0px !important;
}

.full-name,
.username {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 1.2;
}

.full-name {
    font-size: 16px;
    text-overflow: ellipsis;
}

.user-button {
    justify-content: flex-start;
    padding: var(--spacing-xs) var(--spacing-md);
    margin-left: auto;
}
</style>
