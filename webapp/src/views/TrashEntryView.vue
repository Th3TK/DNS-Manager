<script setup lang="ts">
import { NDescriptions, NDescriptionsItem, NFlex, NTag, NText, NTime } from "naive-ui";
import MainLayout from "../layouts/MainLayout.vue";
import useFetch from "../composables/useFetch.ts";
import type { TrashEntry } from "../types/api.types.ts";
import { useRoute, useRouter } from "vue-router";
import { useErrorHandler } from "../composables/useErrorHandler.ts";
import TimeToLiveField from "../components/data-table/fields/TimeToLiveField.vue";
import ActorField from "../components/data-table/fields/ActorField.vue";
import { AxiosError, HttpStatusCode } from "axios";
import TrashControls from "../components/controls/TrashControls.vue";

const route = useRoute();
const router = useRouter();
const { handleError } = useErrorHandler();

const { data: item, error, loading } = useFetch<TrashEntry>(`/trash/${route.params.uuid}`);

if (error.value) {
    handleError(error.value);
}

const navigateToTable = () => {
    router.push({ name: "Trash" });
};

const handleControlsError = (error?: AxiosError) => {
    if (error?.response?.status === HttpStatusCode.NotFound) navigateToTable();
};
</script>

<template>
    <MainLayout>
        <NFlex
            vertical
            v-if="item"
            size="large"
        >
            <NFlex
                justify="space-between"
                align="center"
            >
                <NText
                    tag="h2"
                    class="title"
                >
                    Deleted item
                </NText>
                <TrashControls
                    type="current"
                    :entries="item"
                    @delete-success="navigateToTable"
                    @restore-success="navigateToTable"
                    @delete-error="handleControlsError"
                    @restore-error="handleControlsError"
                />
            </NFlex>

            <NText
                tag="h3"
                class="title"
            >
                Trash metadata
            </NText>
            <NDescriptions
                bordered
                v-if="item"
                :column="1"
                label-placement="left"
                class="descriptions"
            >
                <NDescriptionsItem label="Type">
                    <NTag :bordered="false">
                        {{ item.object_type.toUpperCase() }}
                    </NTag>
                </NDescriptionsItem>
                <NDescriptionsItem label="Deleted by">
                    <ActorField :value="item.actor" />
                </NDescriptionsItem>
                <NDescriptionsItem label="Deleted on">
                    <NTime
                        :time="new Date(item.deletion_timestamp)"
                        format="MMMM do, yyyy 'at' HH:mm"
                    />
                </NDescriptionsItem>
                <NDescriptionsItem label="Permanent deletion on">
                    <NTime
                        :time="new Date(new Date(item.deletion_timestamp).getTime() + 2_592_000_000)"
                        format="MMMM do, yyyy 'at' HH:mm"
                    />
                </NDescriptionsItem>
                <NDescriptionsItem label="Time to live">
                    <TimeToLiveField :deletion-timestamp="new Date(item.deletion_timestamp)" />
                </NDescriptionsItem>
            </NDescriptions>
            <template v-if="item.object_type === 'record'">
                <NText
                    tag="h3"
                    class="title"
                >
                    Record properties
                </NText>

                <NDescriptions
                    bordered
                    :column="1"
                    label-placement="left"
                    class="descriptions"
                >
                    <NDescriptionsItem label="Parent zone">
                        <NText class="monospace">
                            {{ item.object_data.zone_name }}
                        </NText>
                    </NDescriptionsItem>
                    <NDescriptionsItem label="Record name">
                        <NText class="monospace">
                            {{ item.object_data.name }}
                        </NText>
                    </NDescriptionsItem>
                    <NDescriptionsItem label="Record type">
                        <NText class="monospace">
                            {{ item.object_data.type }}
                        </NText>
                    </NDescriptionsItem>
                    <NDescriptionsItem label="Content">
                        <NText class="monospace">
                            {{ item.object_data.content }}
                        </NText>
                    </NDescriptionsItem>
                    <NDescriptionsItem label="TTL">
                        <NText class="monospace"> {{ item.object_data.ttl }} seconds </NText>
                    </NDescriptionsItem>
                    <NDescriptionsItem label="Comment">
                        <NText> {{ item.object_data.comment || "-" }} </NText>
                    </NDescriptionsItem>

                    <NDescriptionsItem label="Checks">
                        <NTag
                            :type="item.object_data.comment ? 'success' : 'warning'"
                            :bordered="false"
                        >
                            {{ item.object_data.comment ? "Enabled" : "Disabled" }}
                        </NTag>
                    </NDescriptionsItem>
                </NDescriptions>
            </template>
            <template v-else-if="item.object_type === 'zone'">
                <NText
                    tag="h3"
                    class="title"
                >
                    Zone properties
                </NText>
                <NDescriptions
                    bordered
                    :column="1"
                    label-placement="left"
                    class="descriptions"
                >
                    <NDescriptionsItem label="Comment">
                        <NText class="monospace"> {{ item.object_data.name || "-" }} </NText>
                    </NDescriptionsItem>
                    <NDescriptionsItem label="Comment">
                        <NText> {{ item.object_data.comment || "-" }} </NText>
                    </NDescriptionsItem>
                </NDescriptions>
            </template>
        </NFlex>
    </MainLayout>
</template>
<style lang="css" scoped>
.title {
    margin: var(--spacing-xs) 0;
}
.header-tag {
    font-size: 16px;
    font-weight: 700;
}
.monospace {
    font-family: monospace;
    text-wrap: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
}
.descriptions :deep(.n-descriptions-table-header) {
    width: 250px;
}
</style>
