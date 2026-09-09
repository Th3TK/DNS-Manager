<script setup lang="ts">
import { Tag } from "@vicons/tabler";
import {
    NButton,
    NCard,
    NCheckbox,
    NFlex,
    NForm,
    NFormItem,
    NIcon,
    NInput,
    NInputNumber,
    NModal,
    NSelect,
    type FormInst,
    type FormRules,
} from "naive-ui";
import type { CreateDNSRecordForm, DNSRecord, SupportedDNSRecordTypes } from "../../types/api.types";
import { onMounted, reactive, ref, useTemplateRef, watch } from "vue";
import {
    contentNormalizationFuncs,
    contentPlaceholders,
    contentSanitizationFuncs,
    isValidDnsZoneNameLength,
    isValidIpv4Address,
    isValidIpv6Address,
    isValidMxContent,
    isValidSrvContent,
    normalizeDnsRecordName,
    sanitizeDnsName,
} from "../../utils/dns";
import { AxiosError, isAxiosError } from "axios";
import { createRecord, modifyRecord } from "../../services/api";
import { useErrorHandler } from "../../composables/useErrorHandler";

const props = defineProps<{
    onSubmit?: (record: DNSRecord) => void;
    zoneName: string;
    modifying?: DNSRecord;
}>();

const { handleError } = useErrorHandler();

const show = defineModel<boolean>("show", { default: false });

const nameInput = useTemplateRef<InstanceType<typeof NInput>>("name-input");

const formRef = ref<FormInst | null>(null);
const nameError = ref<string | undefined>();
const keyError = ref<string | undefined>();

const form = reactive<CreateDNSRecordForm>({
    name: "",
    type: "A",
    content: "",
    ttl: 60,
    comment: "",
    checks_enabled: true,
});

const rules: FormRules = {
    content: [
        {
            required: true,
            message: "Content is required",
            trigger: ["blur", "input"],
        },
        {
            required: true,
            validator: (_rule, value: string) => {
                switch (form.type) {
                    case "CNAME":
                    case "TXT":
                        break;

                    case "A":
                        return isValidIpv4Address(value) || new Error("Invalid IPv4 address");
                    case "AAAA":
                        return isValidIpv6Address(value) || new Error("Invalid IPv6 address");
                    case "MX":
                        return isValidMxContent(value) || new Error("Invalid MX record");
                    case "SRV":
                        return isValidSrvContent(value) || new Error("Invalid SRV record");
                }

                return true;
            },
            trigger: "blur",
        },
    ],
};

const onNameChange = (value: string) => {
    if (!value) {
        nameError.value = "";
        keyError.value = "";
    }
    if (!isValidDnsZoneNameLength(value)) return;
    form.name = sanitizeDnsName(value);
};

const onNameBlur = () => {
    form.name = normalizeDnsRecordName(form.name, props.zoneName);
};

const onTypeChange = () => {
    keyError.value = "";
    form.content = "";
};

const onContentChange = (value: string) => {
    form.content = contentSanitizationFuncs[form.type](value);
};

const onContentBlur = () => {
    form.content = contentNormalizationFuncs[form.type](form.content);
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
        const record = props.modifying
            ? await modifyRecord(props.zoneName, props.modifying?.name, props.modifying?.type, form)
            : await createRecord(props.zoneName, form);

        close();
        props.onSubmit?.(record);
    } catch (error) {
        if (isAxiosError(error)) {
            if (error.response?.status === 409) {
                keyError.value = "A record with this name and type already exists.";
            }
            handleError(error as AxiosError);
        }
    }
};

// reset values
watch([show, () => props.modifying], () => {
    Object.assign(form, {
        name: props.modifying?.name ?? "",
        comment: props.modifying?.comment ?? "",
        type: (props.modifying?.type as SupportedDNSRecordTypes) ?? "A",
        content: [props.modifying?.content].flat()[0] ?? "",
        ttl: props.modifying?.ttl ?? 60,
        checks_enabled: props.modifying?.checks_enabled ?? true,
    });

    nameError.value = undefined;
    keyError.value = undefined;
});

onMounted(() => nameInput.value?.focus());
</script>

<template>
    <NModal v-model:show="show">
        <NCard
            class="modal"
            title="Create a new DNS record"
            :bordered="false"
            role="dialog"
            aria-modal="true"
        >
            <template #header-extra>
                <NIcon
                    :component="Tag"
                    size="24"
                />
            </template>
            <NForm
                ref="formRef"
                :rules="rules"
                :model="form"
                @submit.prevent="onSubmit"
            >
                <NFlex vertical>
                    <NFlex>
                        <NFormItem
                            label="Name"
                            path="name"
                            class="item stretch"
                            content-class="item-content"
                            :validation-status="nameError || keyError ? 'error' : undefined"
                            :feedback="nameError || keyError"
                        >
                            <NInput
                                ref="name-input"
                                placeholder="website.example.com"
                                :value="form.name"
                                @update:value="onNameChange"
                                @blur="onNameBlur"
                                maxlength="253"
                            />
                        </NFormItem>
                        <NFormItem
                            label="Type"
                            path="type"
                            class="item small"
                            content-class="item-content"
                            :validation-status="keyError ? 'error' : undefined"
                        >
                            <NSelect
                                placeholder="Select record type"
                                v-model:value="form.type"
                                @update:value="onTypeChange"
                                :options="['A', 'AAAA', 'CNAME', 'MX', 'SRV', 'TXT'].map((e) => ({ value: e, label: e }))"
                            />
                        </NFormItem>
                    </NFlex>
                    <NFlex>
                        <NFormItem
                            label="Content"
                            path="content"
                            class="item stretch"
                            content-class="item-content"
                        >
                            <NInput
                                ref="name-input"
                                :placeholder="contentPlaceholders[form.type]"
                                :value="form.content"
                                @update:value="onContentChange"
                                @blur="onContentBlur"
                                maxlength="253"
                            />
                        </NFormItem>
                        <NFormItem
                            label="TTL"
                            path="ttl"
                            class="item small"
                            content-class="item-content"
                        >
                            <NInputNumber
                                ref="name-input"
                                v-model:value="form.ttl"
                                :max="2_147_483_647"
                                :min="1"
                                :step="30"
                            />
                        </NFormItem>
                    </NFlex>
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
                    <NFormItem
                        label="Status checks"
                        path="checks_enabled"
                        class="item"
                    >
                        <NCheckbox v-model:checked="form.checks_enabled"> Run periodical status checks </NCheckbox>
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
    width: 600px;
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
.item.stretch {
    flex: 1;
}
.item.small {
    width: 120px;
}
.note {
    font-size: 12px;
}
.button {
    flex: 1;
}
</style>
