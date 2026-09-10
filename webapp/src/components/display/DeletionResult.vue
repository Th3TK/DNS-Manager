<script setup lang="ts" generic="T extends Record<string, any>">
import type { AxiosError } from "axios";
import { NButton, NFlex, NPopover, NScrollbar, NText } from "naive-ui";
import { Help } from "@vicons/tabler";

defineProps<{
    succeeded: number;
    keyField: keyof T;
    failed: {
        object: T;
        error: AxiosError;
    }[];
}>();
</script>

<template>
    <NFlex class="container">
        <NText> {{ succeeded }} succeeded, {{ failed.length }} failed </NText>

        <NPopover
            trigger="hover"
            placement="bottom"
            :z-index="100000"
        >
            <template #trigger>
                <NButton
                    quaternary
                    circle
                    size="small"
                >
                    <template #icon>
                        <Help />
                    </template>
                </NButton>
            </template>

            <NScrollbar style="max-height: 250px; width: 350px">
                <NText
                    v-for="{ object, error } in failed"
                    :key="object[keyField]"
                    style="display: block; padding: 4px 0; font-size: 14px"
                >
                    <NText
                        strong
                        type="error"
                    >
                        {{ object[keyField] }}:
                    </NText>

                    {{
                        // @ts-expect-error
                        error.response?.data?.detail ?? error.message
                    }}
                </NText>
            </NScrollbar>
        </NPopover>
    </NFlex>
</template>

<style lang="css" scoped>
.container {
    align-items: center;
    gap: 0 !important;
}
</style>
