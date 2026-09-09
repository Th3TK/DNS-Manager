<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import useFetch from "../composables/useFetch.ts";
import MainLayout from "../layouts/MainLayout.vue";
import type { DNSRecord } from "../types/api.types.ts";
import { NDescriptions, NDescriptionsItem, NFlex, NTag, NText } from "naive-ui";
import DNSRecordTypeTag from "../components/display/DNSRecordTypeTag.vue";
import { watch } from "vue";
import ActorField from "../components/data-table/fields/ActorField.vue";
import DNSRecordOriginTag from "../components/display/DNSRecordOriginTag.vue";
import { useErrorHandler } from "../composables/useErrorHandler.ts";
import { HttpStatusCode } from "axios";
import RecordControls from "../components/controls/RecordControls.vue";

const route = useRoute();
const router = useRouter();
const { handleError } = useErrorHandler();

const {
    data: record,
    error,
    loading,
    refresh,
} = useFetch<DNSRecord>(
    () => `/zones/${route.params.name}/record?record_name=${route.params.record_name}&record_type=${route.params.record_type}`,
);

const onEdit = async (record: DNSRecord) => {
    if (record.name !== route.params.name || record.type !== route.params.type) {
        await router.replace({
            name: "RecordDetails",
            params: {
                name: record.zone_name,
                record_name: record.name,
                record_type: record.type,
            },
        });
    }
    refresh();
};

const navigateToTable = () => {
    router.push({ name: "ZoneDetails", params: { name: route.params.name } });
};

watch(error, () => {
    if (!error.value) return;

    if (error.value.response?.status === HttpStatusCode.NotFound) {
        router.push(`/zones/${route.params.name}`);
        return;
    }

    handleError(error.value);
});
</script>

<template>
    <MainLayout>
        <NFlex
            vertical
            size="large"
        >
            <NFlex
                class="header"
                v-if="record"
            >
                <DNSRecordTypeTag
                    :value="record.type"
                    class="header-tag"
                    size="large"
                    :label="`${record.type} RECORD`"
                />
                <NText
                    tag="h2"
                    class="title"
                >
                    {{ record.name }}
                </NText>
                <RecordControls
                    type="current"
                    :records="record"
                    :zone-name="record.zone_name"
                    @edit-success="onEdit"
                    @delete-error="refresh"
                    @delete-success="navigateToTable"
                    class="controls"
                />
            </NFlex>
            <NText
                tag="h3"
                class="title"
            >
                Record details
            </NText>

            <NDescriptions
                bordered
                v-if="record"
                :column="1"
                label-placement="left"
                class="record-descriptions"
            >
                <NDescriptionsItem label="Parent zone">
                    <NText class="monospace">
                        {{ record.zone_name }}
                    </NText>
                </NDescriptionsItem>
                <NDescriptionsItem label="Record name">
                    <NText class="monospace">
                        {{ record.name }}
                    </NText>
                </NDescriptionsItem>
                <NDescriptionsItem label="Record type">
                    <NText class="monospace">
                        {{ record.type }}
                    </NText>
                </NDescriptionsItem>
                <NDescriptionsItem label="Content">
                    <NText class="monospace">
                        {{ record.content }}
                    </NText>
                </NDescriptionsItem>
                <NDescriptionsItem label="TTL">
                    <NText class="monospace"> {{ record.ttl }} seconds </NText>
                </NDescriptionsItem>
            </NDescriptions>
            <NText
                tag="h3"
                class="title"
            >
                Record metadata
            </NText>
            <NDescriptions
                bordered
                v-if="record"
                :column="1"
                label-placement="left"
                class="record-descriptions"
            >
                <NDescriptionsItem label="Comment">
                    <NText> {{ record.comment || "-" }} </NText>
                </NDescriptionsItem>

                <NDescriptionsItem
                    label="Created by"
                    :content-style="{ display: 'flex', alignItems: 'center' }"
                >
                    <ActorField :value="record.author" />
                </NDescriptionsItem>

                <NDescriptionsItem label="Origin">
                    <DNSRecordOriginTag :value="record.origin" />
                </NDescriptionsItem>
                <NDescriptionsItem label="Checks">
                    <NTag
                        :type="record.checks_enabled ? 'success' : 'warning'"
                        :bordered="false"
                    >
                        {{ record.checks_enabled ? "Enabled" : "Disabled" }}
                    </NTag>
                </NDescriptionsItem>
            </NDescriptions>
        </NFlex>
    </MainLayout>
</template>

<style lang="css" scoped>
.header {
    width: 100%;
    align-items: center;
}
:deep(.controls) {
    margin-left: auto;
}
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
.record-descriptions :deep(.n-descriptions-table-header) {
    width: 250px;
}
</style>
