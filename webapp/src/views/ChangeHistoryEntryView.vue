<script setup lang="ts">
import { HttpStatusCode, type AxiosError } from "axios";
import MainLayout from "../layouts/MainLayout.vue";
import type { ChangeHistoryEntry } from "../types/api.types.ts";
import useFetch from "../composables/useFetch.ts";
import { useErrorHandler } from "../composables/useErrorHandler.ts";
import { useRoute, useRouter } from "vue-router";
import { NDescriptions, NDescriptionsItem, NFlex, NGrid, NGridItem, NTag, NText, NTime, useThemeVars } from "naive-ui";
import ActionTypeTag from "../components/display/ActionTypeTag.vue";
import ActorField from "../components/data-table/fields/ActorField.vue";
import _ from "lodash";

const route = useRoute();
const router = useRouter();
const themeVars = useThemeVars();
const { handleError } = useErrorHandler();

const { data: entry, error, loading } = useFetch<ChangeHistoryEntry>(`/change-history/${route.params.uuid}`);

if (error.value) {
    handleError(error.value);
}

const navigateToTable = () => {
    router.push({ name: "Trash" });
};

const handleControlsError = (error: AxiosError) => {
    if (error.response?.status === HttpStatusCode.NotFound) navigateToTable();
};

const keyOrder = ["zone_name", "name", "type", "content", "ttl", "origin", "comment", "author", "record_count", "checks_enabled"];

const sortEntries = (o: Record<string, any>) =>
    _.sortBy(_.entries(o), ([key]) => {
        const index = keyOrder.indexOf(key);
        return index === -1 ? Infinity : index;
    });

const isChanged = (field: string, old_: Record<string, any> | null, new_: Record<string, any> | null) =>
    old_ && new_ && !_.isEqual(old_?.[field], new_?.[field]);
</script>

<template>
    <MainLayout>
        <NFlex
            vertical
            v-if="entry"
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
                    Change History Entry
                </NText>
            </NFlex>

            <NText
                tag="h3"
                class="title"
            >
                Entry details
            </NText>
            <NDescriptions
                bordered
                v-if="entry"
                :column="1"
                label-placement="left"
                class="descriptions"
            >
                <NDescriptionsItem label="Action">
                    <ActionTypeTag
                        :value="entry.action"
                        :round="false"
                        size="small"
                    />
                </NDescriptionsItem>
                <NDescriptionsItem label="Affected object type">
                    <NTag
                        :bordered="false"
                        size="small"
                    >
                        {{ entry.affected_object_type.toUpperCase() }}
                    </NTag>
                </NDescriptionsItem>
                <NDescriptionsItem label="Actor">
                    <ActorField :value="entry.actor" />
                </NDescriptionsItem>
                <NDescriptionsItem label="Performed at">
                    <NTime
                        :time="new Date(entry.action_timestamp)"
                        format="MMMM do, yyyy 'at' HH:mm"
                    />
                </NDescriptionsItem>
            </NDescriptions>
            <NFlex>
                <NFlex
                    v-for="(o, index) in [entry.object_before, entry.object_after]"
                    vertical
                    :class="{ 'object-details': true, 'object-details-hidden': !o }"
                >
                    <NText
                        v-if="o"
                        tag="h3"
                        class="title"
                    >
                        {{
                            {
                                created: "Created object",
                                restored: "Restored object",
                                deleted: "Deleted object",
                                permanently_deleted: "Permanently deleted object",
                                changed: index ? "Object after" : "Object before",
                            }[entry.action]
                        }}
                    </NText>
                    <NDescriptions
                        v-if="o"
                        bordered
                        :column="1"
                        label-placement="left"
                        class="descriptions"
                    >
                        <NDescriptionsItem
                            v-for="[field, value] in sortEntries(o)"
                            :label="field"
                        >
                            <NText
                                class="monospace"
                                :style="{
                                    color: isChanged(field, entry.object_before, entry.object_after) ? themeVars.warningColor : undefined,
                                }"
                            >
                                {{ value }}
                            </NText>
                        </NDescriptionsItem>
                    </NDescriptions>
                </NFlex>
            </NFlex>
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
    text-overflow: ellipsis;
    overflow: hidden;
}
.descriptions :deep(.n-descriptions-table-header) {
    width: 250px;
}
.object-details {
    flex: 1;
}
.object-details-hidden {
    display: none !important;
}
.changed {
    color: var(--n-warning-color);
}
</style>
