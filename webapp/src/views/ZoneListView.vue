<script setup lang="ts">
import type { AxiosError } from "axios";
import { useErrorHandler } from "../composables/useErrorHandler.ts";
import useFetch from "../composables/useFetch.ts";
import ZonesTable from "../features/zone/ZonesTable.vue";
import MainLayout from "../layouts/MainLayout.vue";
import type { DNSZone } from "../types/api.types.ts";

const { handleError } = useErrorHandler();
</script>

<template>
    <MainLayout>
        <ZonesTable />
    </MainLayout>
</template>
