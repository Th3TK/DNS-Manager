<script setup lang="ts">
import _ from "lodash";
import { NTag, type TagProps } from "naive-ui";
import { computed } from "vue";

const props = defineProps<{
    value: string;
    variants?: Record<string, TagProps>;
    default?: TagProps;
}>();

const passedProps = computed(() => _.merge(props.default, props.variants?.[props.value]));
</script>

<template>
    <NTag
        v-bind="passedProps"
        @dblclick.stop
    >
        {{ props.value }}
    </NTag>
</template>
