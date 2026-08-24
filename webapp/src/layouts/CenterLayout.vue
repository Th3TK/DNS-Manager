<script setup lang="ts">
import { NLayout, NLayoutContent } from "naive-ui";
</script>

<template>
    <NLayout class="layout">
        <NLayoutContent class="content">
            <slot />
        </NLayoutContent>
    </NLayout>
</template>

<style scoped>
.layout {
    min-height: 100vh;
}

.content {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
