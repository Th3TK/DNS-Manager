<script setup lang="ts">
import { useRoute } from "vue-router";
import MainLayout from "../layouts/MainLayout.vue";
import useFetch from "../composables/useFetch.ts";
import type { Record, Zone } from "../types/api.types.ts";
import { NDescriptions, NDescriptionsItem, NIcon, NText, NThing } from "naive-ui";
import { World } from "@vicons/tabler";
import RecordsTable from "../features/records/RecordsTable.vue";
const route = useRoute();

const { data: zone, error: zoneError, loading: zoneLoading } = useFetch<Zone>(`/zones/${route.params.name}`);
const { data: records, error: recordsError, loading: recordsLoading } = useFetch<Record[]>(`/zones/${route.params.name}/records`);
</script>

<template>
    <MainLayout>
        <NThing
            v-if="zone"
            class="description"
        >
            <template #avatar>
                <NIcon
                    :component="World"
                    size="30"
                />
            </template>
            <template #header>
                <NText
                    tag="h2"
                    class="header"
                >
                    {{ zone.name }}
                </NText>
            </template>

            <NDescriptions label-placement="top">
                <NDescriptionsItem label="Comment">
                    {{ zone.comment ?? "-" }}
                </NDescriptionsItem>
                <NDescriptionsItem label="Author">
                    {{ zone.author ?? "-" }}
                </NDescriptionsItem>
                <NDescriptionsItem label="Origin">
                    {{ zone.origin }}
                </NDescriptionsItem>
            </NDescriptions>
        </NThing>
        <RecordsTable :data="records ?? []" />
    </MainLayout>
</template>

<style lang="css" scoped>
.header {
    margin: 0;
}
.description {
    margin-bottom: var(--spacing-lg);
}
</style>
