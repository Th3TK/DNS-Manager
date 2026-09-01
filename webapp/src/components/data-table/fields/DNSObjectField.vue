<script setup lang="ts">
import { NText } from "naive-ui";
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
    <NText @click.stop>
        {{ type == "zone" ? data.name : `${data.name} ${data.type} ${data.content}` }}
    </NText>
    <NText
        @click.stop
        depth="3"
    >
        {{ data.comment }}
    </NText>
</template>
