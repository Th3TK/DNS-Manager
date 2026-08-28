<script setup lang="ts" generic="T extends Record<string, any>">
import _ from "lodash";
import { computed, reactive, ref } from "vue";
import { NButton, NCheckbox, NFlex, NInput, NPopover, NSelect, NTag, type DataTableColumns } from "naive-ui";
import type { FilterConfig, Filters } from "../../../types/table.types";
import type { SelectMixedOption } from "naive-ui/es/select/src/interface";

const props = defineProps<{
    columns: DataTableColumns<T>;
    filterConfig: Record<keyof T, FilterConfig>;
}>();

const filters = defineModel<Filters<T>>();

// selected field
const field = ref<string | null>(null);

// draft values for the filters
const draft = reactive<{
    freetext: string;
    options: Record<string, boolean>;
}>({
    freetext: "",
    options: {},
});

// prettier-ignore
const fields = computed<SelectMixedOption[]>(() =>
    props.columns
        .filter((col) =>
            "key" in col &&
            "title" in col &&
            col.key in props.filterConfig &&
            !(col.key in (filters.value ?? {}))
        )
        .map((col) => ({
            // @ts-expect-error
            label: col.title,
            // @ts-expect-error
            value: col.key,
        })),
);

// filter config for the currently set field
const selectedConfig = computed<FilterConfig | null>(() => {
    if (field.value === null) return null;
    return props.filterConfig[field.value as keyof T] ?? null;
});

// when field gets selected, reset the state
const onSelectField = (value: string | null) => {
    field.value = value;
    draft.freetext = "";
    draft.options = {};
};

// on filter creation
const submit = () => {
    if (_.isNull(field.value) || _.isNull(selectedConfig.value)) return;

    const key = field.value as keyof T;
    const type = selectedConfig.value.type;
    const value = draft[type];

    if (_.isEmpty(value)) return;

    const getValueToAssign = {
        freetext: () => value,
        options: () => _.keys(_.pickBy(value, Boolean)),
    };

    filters.value = {
        ...filters.value,
        [key]: getValueToAssign[type](),
    } as Filters<T>;

    onSelectField(null);
};
</script>

<template>
    <NPopover
        v-if="!_.isEmpty(fields)"
        trigger="click"
        placement="bottom-start"
    >
        <template #trigger>
            <NTag
                :bordered="false"
                class="button"
                type="primary"
            >
                + Add filter
            </NTag>
        </template>

        <NFlex
            vertical
            style="width: 240px"
            size="medium"
        >
            <NSelect
                :value="field"
                :options="fields"
                placeholder="Select field"
                @update:value="onSelectField"
            />

            <NInput
                v-if="selectedConfig?.type === 'freetext'"
                v-model:value="draft.freetext"
                placeholder="Enter value"
            />
            <NFlex
                v-else-if="selectedConfig?.type === 'options'"
                vertical
                size="small"
            >
                <NCheckbox
                    v-for="option in selectedConfig.options"
                    :key="option.value"
                    v-model:checked="draft.options[option.value]"
                    :label="option.label"
                />
            </NFlex>

            <NButton
                type="primary"
                block
                :disabled="!field || !selectedConfig || _.isEmpty(draft[selectedConfig.type])"
                @click="submit"
            >
                Submit
            </NButton>
        </NFlex>
    </NPopover>
</template>

<style lang="css" scoped>
.button:hover {
    cursor: pointer;
}
</style>
