<script setup lang="ts">
import { NFlex, NTag, NText } from "naive-ui";
import type { DNSRecord, DNSZone } from "../../../types/api.types";

const props = defineProps<
    | {
          data: Partial<DNSZone>;
          type: "zone";
      }
    | {
          data: Partial<DNSRecord>;
          type: "record";
      }
>();
</script>

<template>
    <NFlex
        vertical
        class="container"
    >
        <NText
            class="key"
            v-if="type === 'zone'"
            @click.stop
        >
            {{ data.name }}
        </NText>
        <NFlex
            v-else
            :size="12"
            align="center"
            @click.stop
        >
            <NText class="key">{{ data.name }}</NText>
            <NText class="key">{{ data.type }}</NText>
            <NText class="key">{{ data.content }}</NText>
        </NFlex>
        <NText
            v-if="data.comment"
            @click.stop
            depth="3"
            class="comment"
        >
            Comment: {{ data.comment }}
        </NText>
    </NFlex>
</template>

<style lang="css" scoped>
.container {
    width: fit-content;
}
.comment {
    text-overflow: ellipsis;
    overflow: hidden;
}
.key {
    font-family: monospace;
    white-space: pre;
}
</style>
