<script setup lang="ts">
import { AxiosError } from "axios";

import type { DNSZone } from "../../types/api.types.ts";

import ConfirmationModal from "../modals/ConfirmationModal.vue";
import { useZoneActions } from "../../composables/useZoneActions.ts";
import ZoneDropdownControls from "./zone/ZoneDropdownControls.vue";
import ZoneButtonControls from "./zone/ZoneButtonControls.vue";
import _ from "lodash";
import CreateZoneModal from "../modals/CreateZoneModal.vue";
import ZoneTableControls from "./zone/ZoneTableControls.vue";
import { NText } from "naive-ui";
import { toRef } from "vue";

defineOptions({
    inheritAttrs: false,
});

const props = defineProps<{
    zones: DNSZone | DNSZone[];
    dropdown?: boolean;
    onDeleteError?: (error: AxiosError) => void;
    onDeleteSuccess?: () => void;
    onCreateSuccess?: (zone: DNSZone) => void;
}>();

const zones = toRef(props, "zones");

const { deleteModalOpened, createModalOpened, onDelete, onNavigate } = useZoneActions(zones, props.onDeleteSuccess, props.onDeleteError);
</script>

<template>
    <ZoneDropdownControls
        v-if="dropdown && !_.isArray(zones)"
        v-bind="$attrs"
        @navigate="onNavigate"
        @delete="deleteModalOpened = true"
    />
    <ZoneButtonControls
        v-else-if="!_.isArray(zones)"
        v-bind="$attrs"
        @delete="deleteModalOpened = true"
    />
    <ZoneTableControls
        v-else
        v-bind="$attrs"
        @delete="deleteModalOpened = true"
        @create="createModalOpened = true"
        :show-delete="Boolean(zones.length)"
    />

    <ConfirmationModal
        type="error"
        v-model:show="deleteModalOpened"
        @submit="onDelete"
    >
        <template #title> Zone deletion </template>
        <template
            #description
            v-if="_.isArray(zones)"
        >
            <NText>
                Selected zones ({{ zones.length }}) will be deleted along with
                <NText type="error"> all of their records ({{ _.sum(zones.map((z) => z.record_count)) }}). </NText>
            </NText>
            <NText>
                The zones and their internal records will be moved to trash, while
                <NText type="error">external records will be permanently deleted.</NText>
            </NText>
        </template>
        <template
            #description
            v-else
        >
            <NText>
                Selected zone will be deleted along with
                <NText type="error"> all of its records ({{ zones.record_count }}). </NText>
            </NText>
            <NText>
                The zone and its internal records will be moved to trash, while
                <NText type="error">external records will be permanently deleted.</NText>
            </NText>
        </template>
    </ConfirmationModal>
    <CreateZoneModal
        v-model:show="createModalOpened"
        @submit="onCreateSuccess"
    />
</template>
