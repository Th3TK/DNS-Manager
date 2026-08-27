<script setup lang="ts">
import type { AxiosError } from "axios";
import { useErrorHandler } from "../composables/useErrorHandler.ts";
import useFetch from "../composables/useFetch.ts";
import ZonesTable from "../features/zone/ZonesTable.vue";
import MainLayout from "../layouts/MainLayout.vue";
import type { Zone } from "../types/api.types.ts";

const { handleError } = useErrorHandler();
const { data, error, loading } = useFetch<Zone[]>("zones");

if (error.value) {
    handleError(error.value);
}
</script>

<template>
    <MainLayout>
        <ZonesTable :data="data ?? []" />
    </MainLayout>
</template>
