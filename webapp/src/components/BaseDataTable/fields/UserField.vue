<script setup lang="ts">
import type { User } from "../../../types/api.types";

const props = defineProps<{
    user: User;
}>();
</script>

<template>
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
</template>

<style scoped>
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
</style>
