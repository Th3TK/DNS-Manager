<script setup lang="ts">
import { Key } from "@vicons/tabler";
import { NButton, NCard, NFlex, NForm, NFormItem, NIcon, NInput, NModal, type FormInst, type FormItemRule, type FormRules } from "naive-ui";
import type { ChangePasswordForm } from "../../types/api.types";
import { onMounted, reactive, ref, useTemplateRef, watch } from "vue";
import { AxiosError } from "axios";
import { changeOwnPassword, changeUserPassword } from "../../services/api";
import { useErrorHandler } from "../../composables/useErrorHandler";

const props = defineProps<{
    username: string;
    currentUser?: boolean;
    onSubmit?: () => void;
}>();

const { handleError } = useErrorHandler();

const show = defineModel<boolean>("show", { default: false });

const formRef = ref<FormInst | null>(null);
const passwordInput = useTemplateRef<InstanceType<typeof NInput>>("password-input");
const confirmPasswordItem = useTemplateRef<InstanceType<typeof NFormItem>>("confirm-password-item");

const form = reactive<ChangePasswordForm & { confirm_password: string }>({
    password: "",
    confirm_password: "",
});

const validatePasswordEqual = (rule: FormItemRule, value: string): boolean => !form.password || value === form.password;

const rules: FormRules = {
    password: {
        required: true,
        validator: (r, val) => val.length >= 6,
        message: "Password must be at least 6 characters long.",
        trigger: "blur",
    },
    confirm_password: [
        {
            required: true,
            message: "Re-entered password is required.",
            trigger: ["input", "blur"],
        },
        {
            validator: validatePasswordEqual,
            message: "Passwords do not match.",
            trigger: ["blur", "password-input"],
        },
    ],
};

const onPasswordChange = (value: string) => {
    if (!value) return;
    confirmPasswordItem.value?.validate({ trigger: "password-input" });
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
        const { confirm_password, ...data } = form;

        if (props.currentUser) {
            await changeOwnPassword(data);
        } else {
            await changeUserPassword(props.username, data);
        }

        close();
        props.onSubmit?.();
    } catch (error) {
        handleError(error as AxiosError);
    }
};

watch(show, () => {
    form.password = "";
    form.confirm_password = "";
});

onMounted(() => passwordInput.value?.focus());
</script>

<template>
    <NModal v-model:show="show">
        <NCard
            class="modal"
            title="Change Password"
            :bordered="false"
            role="dialog"
            aria-modal="true"
        >
            <template #header-extra>
                <NIcon
                    :component="Key"
                    size="24"
                />
            </template>
            <NForm
                ref="formRef"
                :model="form"
                :rules="rules"
                @submit.prevent="onSubmit"
            >
                <NFlex
                    vertical
                    size="small"
                >
                    <NFormItem
                        label="Password"
                        path="password"
                        class="item"
                    >
                        <NInput
                            ref="password-input"
                            v-model:value="form.password"
                            @update:value="onPasswordChange"
                            type="password"
                            maxlength="128"
                            placeholder="Enter password"
                        >
                        </NInput>
                    </NFormItem>
                    <NFormItem
                        ref="confirm-password-item"
                        label="Confirm password"
                        path="confirm_password"
                        class="item"
                    >
                        <NInput
                            v-model:value="form.confirm_password"
                            type="password"
                            minlength="6"
                            maxlength="128"
                            placeholder="Confirm password"
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
