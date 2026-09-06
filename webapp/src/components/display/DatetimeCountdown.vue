<script setup lang="ts">
import { computed } from "vue";
import { NCountdown, NText } from "naive-ui";

const props = defineProps<{
    label?: string;
    datetime: Date;
}>();

const duration = computed(() => Math.max(0, props.datetime.getTime() - Date.now()));
</script>

<template>
    <NText>
        {{ label }}
        <NCountdown :duration="duration" />
    </NText>
</template>
<style scoped></style>
