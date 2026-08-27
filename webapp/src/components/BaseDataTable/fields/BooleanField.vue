<script setup lang="ts">
import { NText } from "naive-ui";

const props = defineProps<{
    value: boolean;
    onTrue?: string;
    onFalse?: string;
}>();
</script>

<template>
    <NText @click.stop>
        {{ value ? (onTrue ?? "Yes") : (onFalse ?? "No") }}
    </NText>
</template>
