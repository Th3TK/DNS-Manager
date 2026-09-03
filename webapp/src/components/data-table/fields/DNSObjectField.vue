<script setup lang="ts">
import { NFlex, NText } from "naive-ui";
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
    <NFlex vertical>
        <NText @click.stop>
            {{ type == "zone" ? data.name : `${data.name} ${data.type} ${data.content}` }}
        </NText>
        <!-- <NText
            @click.stop
            depth="3"
            class="comment"
        >
            {{ data.comment }}
        </NText> -->
    </NFlex>
</template>

<style lang="css" scoped>
.comment {
    text-wrap: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
}
</style>
