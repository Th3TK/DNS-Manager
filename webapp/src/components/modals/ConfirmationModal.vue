<script setup lang="ts">
import { AlertTriangle } from "@vicons/tabler";
import { NButton, NCard, NFlex, NIcon, NModal, NText } from "naive-ui";

const props = defineProps<{
    onSubmit: () => unknown;
    type: "error" | "info" | "primary" | "warning";
}>();

const show = defineModel("show", { default: false });

const close = () => (show.value = false);

const onSubmit = () => {
    props.onSubmit();
    close();
};
</script>

<template>
    <NModal v-model:show="show">
        <NCard
            class="modal"
            role="dialog"
            aria-modal="true"
            :bordered="false"
        >
            <template #header>
                <NText
                    :type="type"
                    class="title"
                >
                    <NIcon
                        v-if="type === 'error'"
                        :component="AlertTriangle"
                        size="22"
                    />
                    <slot name="title" />
                </NText>
            </template>
            <NFlex
                vertical
                size="large"
            >
                <slot name="description" />
                <NText> Are you sure you want to continue? </NText>
                <NFlex class="buttons">
                    <NButton
                        type="default"
                        class="button"
                        secondary
                        @click="close"
                    >
                        Cancel
                    </NButton>
                    <NButton
                        :type="type"
                        class="button"
                        @click="onSubmit"
                        strong
                    >
                        Confirm
                    </NButton>
                </NFlex>
            </NFlex>
        </NCard>
    </NModal>
</template>

<style scoped>
.modal {
    width: 480px;
    position: fixed;
    top: var(--spacing-xl);
    left: 50%;
    transform: translateX(-50%);
}
.buttons {
    margin-top: var(--spacing-md);
}
.button {
    flex: 1;
}
.title {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}
</style>
