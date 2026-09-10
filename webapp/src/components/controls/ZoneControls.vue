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
import { computed, toRef } from "vue";

defineOptions({
    inheritAttrs: false,
});

const props = defineProps<{
    zones: DNSZone | DNSZone[];
    type: "dropdown" | "current" | "table";
    onDeleteError?: (error?: AxiosError) => void;
    onDeleteSuccess?: () => void;
    onCreateSuccess?: (zone: DNSZone) => void;
}>();

const zones = toRef(props, "zones");

const { deleteModalOpened, createModalOpened, onDelete, onNavigate } = useZoneActions(props.onDeleteSuccess, props.onDeleteError);

const zonesList = computed(() => [zones.value].flat());
const zone = computed(() => (_.isArray(zones.value) ? null : zones.value));
</script>

<template>
    <ZoneDropdownControls
        v-if="type === 'dropdown' && zone"
        v-bind="$attrs"
        @navigate="() => onNavigate(zone as DNSZone)"
        @delete="deleteModalOpened = true"
    />
    <ZoneButtonControls
        v-else-if="type === 'current' && zone"
        v-bind="$attrs"
        @delete="deleteModalOpened = true"
    />
    <ZoneTableControls
        v-else-if="type === 'table'"
        v-bind="$attrs"
        @delete="deleteModalOpened = true"
        @create="createModalOpened = true"
        :show-delete="Boolean(zonesList.length)"
    />

    <ConfirmationModal
        v-if="!_.isEmpty(zones)"
        type="error"
        v-model:show="deleteModalOpened"
        @submit="() => onDelete(zonesList)"
    >
        <template #title> Zone deletion </template>
        <template
            #description
            v-if="zonesList.length > 1"
        >
            <NText>
                Selected zones ({{ zonesList.length }}) will be deleted along with
                <NText type="error">
                    all of their records ({{
                        zonesList.find((z) => z.record_count === null) ? "Unknown" : _.sum(zonesList.map((z) => z.record_count))
                    }}).
                </NText>
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
                <NText type="error"> all of its records ({{ zonesList[0].record_count }}). </NText>
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
