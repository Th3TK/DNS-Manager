<script setup lang="ts">
import { World } from "@vicons/tabler";
import { NButton, NCard, NFlex, NForm, NFormItem, NIcon, NInput, NModal, NText, type FormInst } from "naive-ui";
import type { CreateDNSZoneForm, DNSZone } from "../../types/api.types";
import { onMounted, reactive, ref, useTemplateRef, watch } from "vue";
import _ from "lodash";
import { isValidDnsZoneNameLength, normalizeDnsName, sanitizeDnsName } from "../../utils/dns";
import { AxiosError, isAxiosError } from "axios";
import { createZone } from "../../services/api";
import { useErrorHandler } from "../../composables/useErrorHandler";

const props = defineProps<{
    onSubmit?: (zone: DNSZone) => void;
}>();

const { handleError } = useErrorHandler();

const show = defineModel<boolean>("show", { default: false });

const nameInput = useTemplateRef<InstanceType<typeof NInput>>("name-input");

const form = reactive<CreateDNSZoneForm>({
    name: "",
    comment: "",
});

const formRef = ref<FormInst | null>(null);
const nameError = ref<string | undefined>();

const onNameChange = (value: string) => {
    if (value) nameError.value = "";
    if (!isValidDnsZoneNameLength(value)) return;
    form.name = sanitizeDnsName(value);
};

const onNameBlur = () => {
    if (!form.name) nameError.value = "Name is required";
    form.name = normalizeDnsName(form.name);
};

const close = () => {
    show.value = false;
};

const onSubmit = async () => {
    try {
        await formRef.value?.validate();
    } catch {
        return;
    }

    try {
        const zone = await createZone(form);

        close();
        props.onSubmit?.(zone);
    } catch (error) {
        if (isAxiosError(error) && error.response?.status === 409) {
            nameError.value = "A zone with this name already exists.";
        }
        handleError(error as AxiosError);
    }
};

watch(show, () => {
    form.name = "";
    form.comment = "";
    nameError.value = undefined;
});

onMounted(() => nameInput.value?.focus());
</script>

<template>
    <NModal v-model:show="show">
        <NCard
            class="modal"
            title="Create a new DNS zone"
            :bordered="false"
            role="dialog"
            aria-modal="true"
        >
            <template #header-extra>
                <NIcon
                    :component="World"
                    size="24"
                />
            </template>
            <NForm
                ref="formRef"
                @submit.prevent="onSubmit"
            >
                <NFlex vertical>
                    <NFormItem
                        label="Name"
                        path="name"
                        class="item"
                        content-class="item-content"
                        :validation-status="nameError ? 'error' : undefined"
                        :feedback="nameError"
                    >
                        <NInput
                            ref="name-input"
                            placeholder="e.g. example.com"
                            :value="form.name"
                            @update:value="onNameChange"
                            @blur="onNameBlur"
                            maxlength="253"
                        />
                    </NFormItem>

                    <NFormItem
                        label="Comment"
                        path="comment"
                        class="item"
                    >
                        <NInput
                            type="textarea"
                            maxlength="1000"
                            show-count
                            placeholder="Enter an optional comment."
                            v-model:value="form.comment"
                        />
                    </NFormItem>
                    <NFlex>
                        <NButton
                            type="error"
                            class="button"
                            secondary
                            @click="close"
                        >
                            Cancel
                        </NButton>
                        <NButton
                            type="success"
                            class="button"
                            secondary
                            attr-type="submit"
                        >
                            Submit
                        </NButton>
                    </NFlex>
                </NFlex>
            </NForm>
        </NCard>
    </NModal>
</template>

<style scoped>
.modal {
    width: 400px;
}
:deep(.item-content) {
    display: flex;
    flex-direction: column;
    align-items: start;
    gap: var(--spacing-xs);
}
.item :deep(.n-form-item-label) {
    font-weight: 800;
    font-size: 14px;
}
.note {
    font-size: 12px;
}
.button {
    flex: 1;
}
</style>
