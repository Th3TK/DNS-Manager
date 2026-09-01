<script setup lang="ts">
import { NText, NTime } from "naive-ui";

const props = defineProps<{
    value: Date;
}>();

console.log(props.value);
</script>

<template>
    <NText @click.stop>
        <NTime
            :time="value"
            type="datetime"
        />
    </NText>
</template>
