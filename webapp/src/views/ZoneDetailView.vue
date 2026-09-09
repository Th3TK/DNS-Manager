<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import MainLayout from "../layouts/MainLayout.vue";
import useFetch from "../composables/useFetch.ts";
import type { DNSZone } from "../types/api.types.ts";
import { NButton, NCard, NDescriptions, NDescriptionsItem, NFlex, NIcon, NTag, NText } from "naive-ui";
import { ChevronUp, ChevronDown } from "@vicons/tabler";
import RecordsTable from "../components/tables/records/RecordsTable.vue";
import { ref, watch } from "vue";
import ActorField from "../components/data-table/fields/ActorField.vue";
import { useErrorHandler } from "../composables/useErrorHandler.ts";
import { HttpStatusCode } from "axios";
import ZoneControls from "../components/controls/ZoneControls.vue";

const route = useRoute();
const router = useRouter();
const { handleError } = useErrorHandler();

const { data: zone, error, loading } = useFetch<DNSZone>(`/zones/${route.params.name}`);

const detailsHidden = ref(false);

const toggle = () => (detailsHidden.value = !detailsHidden.value);

const navigateToTable = () => {
    router.push({ name: "Zones" });
};

watch(error, () => {
    if (!error.value) return;

    if (error.value.response?.status === HttpStatusCode.NotFound) {
        navigateToTable();
        return;
    }

    handleError(error.value);
});
</script>

<template>
    <MainLayout :class="{ hidden: detailsHidden }">
        <NFlex
            vertical
            size="large"
        >
            <NFlex class="header">
                <NTag
                    :bordered="false"
                    type="primary"
                    class="header-tag"
                    size="large"
                >
                    DNS ZONE
                </NTag>
                <NText
                    tag="h2"
                    class="title"
                >
                    {{ zone?.name }}
                </NText>
                <ZoneControls
                    v-if="zone"
                    type="current"
                    :zones="zone"
                    class="controls"
                    @delete-success="navigateToTable"
                />
            </NFlex>

            <NDescriptions
                bordered
                :column="1"
                label-placement="left"
                class="descriptions"
            >
                <NDescriptionsItem label="Comment">
                    <NText> {{ zone?.comment || "-" }} </NText>
                </NDescriptionsItem>

                <NDescriptionsItem
                    label="Created by"
                    :content-style="{ display: 'flex', alignItems: 'center' }"
                >
                    <ActorField :value="zone?.author" />
                </NDescriptionsItem>
            </NDescriptions>
        </NFlex>

        <template #portal>
            <NCard class="tableCard">
                <RecordsTable
                    v-if="route.params.name"
                    :zone-name="String(route.params.name)"
                    :global="false"
                >
                    <template #header>
                        <NButton
                            class="expandButton"
                            @click="toggle"
                            quaternary
                        >
                            <template #icon>
                                <NIcon
                                    :component="detailsHidden ? ChevronDown : ChevronUp"
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
    width: 100%;
    align-items: center;
}
.title {
    margin: var(--spacing-xs) 0;
}

.header-tag {
    font-size: 16px;
    font-weight: 700;
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
.descriptions :deep(.n-descriptions-table-header) {
    width: 250px;
}
:deep(.controls) {
    margin-left: auto;
}
</style>
