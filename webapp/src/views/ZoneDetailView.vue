<script setup lang="ts">
import { useRoute } from "vue-router";
import MainLayout from "../layouts/MainLayout.vue";
import useFetch from "../composables/useFetch.ts";
import type { DNSZone } from "../types/api.types.ts";
import { NButton, NCard, NDescriptions, NDescriptionsItem, NFlex, NIcon, NTag, NText, NThing } from "naive-ui";
import { World as IconWorld, Maximize, Minimize } from "@vicons/tabler";
import RecordsTable from "../components/tables/records/RecordsTable.vue";
import { ref } from "vue";
const route = useRoute();

const { data: zone, error: zoneError, loading: zoneLoading } = useFetch<DNSZone>(`/zones/${route.params.name}`);

const detailsHidden = ref(false);

const toggle = () => (detailsHidden.value = !detailsHidden.value);
</script>

<template>
    <MainLayout :class="{ hidden: detailsHidden }">
        <NThing
            v-if="zone"
            class="description"
        >
            <template #avatar>
                <NIcon
                    :component="IconWorld"
                    size="30"
                />
            </template>
            <template #header>
                <NFlex align="center">
                    <NText
                        tag="h2"
                        class="header"
                    >
                        {{ zone.name }}
                    </NText>
                    <NTag
                        :bordered="false"
                        :round="true"
                        :type="zone.origin == 'manual' ? 'primary' : 'default'"
                        :style="{ textTransform: 'capitalize' }"
                    >
                        {{ zone.origin }}
                    </NTag>
                </NFlex>
            </template>

            <NDescriptions
                label-placement="top"
                :column="1"
            >
                <NDescriptionsItem label="Comment">
                    <NText
                        class="name"
                        ellipsis
                    >
                        {{ zone.comment ?? "-" }}
                    </NText>
                </NDescriptionsItem>
                <NDescriptionsItem label="Created by">
                    <NText
                        class="name"
                        ellipsis
                    >
                        {{ zone.author ?? "-" }}
                    </NText>
                </NDescriptionsItem>
            </NDescriptions>
        </NThing>
        <template #portal>
            <NCard class="tableCard">
                <RecordsTable :zone-name="String(route.params.name)">
                    <template #header>
                        <NButton
                            class="expandButton"
                            @click="toggle"
                            quaternary
                        >
                            <template #icon>
                                <NIcon
                                    :component="detailsHidden ? Minimize : Maximize"
                                    size="24"
                                />
                            </template>
                        </NButton>
                    </template>
                </RecordsTable>
            </NCard>
        </template>
    </MainLayout>
</template>

<style lang="css" scoped>
.header {
    margin: 0;
}
.description {
    margin-bottom: var(--spacing-lg);
}
.tableCard {
    flex: 3;
}
.expandButton {
    margin-left: auto;
    aspect-ratio: 1/1;
}
:deep(.hidden) {
    display: none;
}
</style>
