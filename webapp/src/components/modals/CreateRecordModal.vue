<script setup lang="ts">
import { ArrowRightBar } from "@vicons/tabler";
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
    isValidDnsZoneNameLength,
    isValidIpv6Address,
    isValidMxContent,
    isValidSrvContent,
    normalizeDnsName,
    normalizeDnsRecordName,
    normalizeMxContent,
    normalizeSrvContent,
    sanitazeIpv4Address,
    sanitizeDnsName,
    sanitizeIpv6Address,
    sanitizeMxContent,
    sanitizeSrvContent,
} from "../../services/dns";
import { isAxiosError } from "axios";
import { createRecord } from "../../services/api";

const props = defineProps<{
    onSubmit?: (zone: DNSRecord) => void;
    zoneName: string;
}>();

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
                    // handled by field sanitization
                    case "A":
                    // handled by field sanitization
                    case "CNAME":
                    //
                    case "TXT":
                        break;

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
};

const contentSanitizationFuncs: Record<SupportedDNSRecordTypes, (val: string) => string> = {
    A: sanitazeIpv4Address,
    AAAA: sanitizeIpv6Address,
    CNAME: sanitizeDnsName,
    MX: sanitizeMxContent,
    SRV: sanitizeSrvContent,
    TXT: (v) => v,
};

const contentNormalizationFuncs: Record<SupportedDNSRecordTypes, (val: string) => string> = {
    A: (v) => v,
    AAAA: (v) => v,
    CNAME: normalizeDnsName,
    MX: normalizeMxContent,
    SRV: normalizeSrvContent,
    TXT: (v) => v,
};

const contentPlaceholders: Record<SupportedDNSRecordTypes, string> = {
    A: "e.g. 192.168.1.1",
    AAAA: "e.g. 2001:db8::1",
    CNAME: "e.g. target.example.com.",
    TXT: 'e.g. "v=spf1 include:example.com ~all"',
    MX: "e.g. 10 mail.example.com.",
    SRV: "e.g. 10 5 5060 sip.example.com.",
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
        const zone = await createRecord(props.zoneName, form);

        close();
        props.onSubmit?.(zone);
    } catch (error) {
        if (isAxiosError(error) && error.response?.status === 409) {
            keyError.value = "A record with this name and type already exists.";
        }
    }
};

watch(show, () => {
    form.name = "";
    form.comment = "";
    form.type = "A";
    form.content = "";
    form.ttl = 60;
    form.checks_enabled = true;
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
                    :component="ArrowRightBar"
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
