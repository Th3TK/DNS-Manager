<script setup lang="ts">
import { UserPlus } from "@vicons/tabler";
import {
    NButton,
    NCard,
    NCheckbox,
    NFlex,
    NForm,
    NFormItem,
    NIcon,
    NInput,
    NModal,
    NSelect,
    type FormInst,
    type FormItemRule,
    type FormRules,
} from "naive-ui";
import type { CreateUserForm, User } from "../../types/api.types";
import { onMounted, reactive, ref, useTemplateRef, watch } from "vue";
import { AxiosError, HttpStatusCode, isAxiosError } from "axios";
import { createUser } from "../../services/api";
import { useErrorHandler } from "../../composables/useErrorHandler";
import { sanitizeUsername } from "../../utils/users";

const props = defineProps<{
    onSubmit?: (user: User) => void;
}>();

const { handleError } = useErrorHandler();

const show = defineModel<boolean>("show", { default: false });

const usernameInput = useTemplateRef<InstanceType<typeof NInput>>("username-input");
const confirmPasswordItem = useTemplateRef<InstanceType<typeof NFormItem>>("confirm-password-item");

const formRef = ref<FormInst | null>(null);
const usernameError = ref<string | undefined>();

const form = reactive<CreateUserForm & { confirm_password: string }>({
    username: "",
    full_name: "",
    password: "",
    confirm_password: "",
    disabled: false,
    is_admin: false,
});

const validatePasswordEqual = (rule: FormItemRule, value: string): boolean => !form.password || value === form.password;

const rules: FormRules = {
    username: [
        {
            required: true,
            validator: (r, val) => val.length >= 3,
            message: "Username must be at least 3 characters long.",
            trigger: ["blur"],
        },

        {
            validator: (r, val) => !["system", "automatic", "deleted"].includes(val),
            message: `That username is reserved.`,
            trigger: ["blur", "input"],
        },
        {
            validator: (r, val) => !val.startsWith("watcher"),
            message: 'Username cannot start with "watcher".',
            trigger: ["blur", "input"],
        },
    ],
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

const onUsernameChange = (value: string) => {
    form.username = sanitizeUsername(value);
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

        const user = await createUser(data);

        close();
        props.onSubmit?.(user);
    } catch (error) {
        if (isAxiosError(error) && error.response?.status === HttpStatusCode.Conflict) {
            usernameError.value = "A user with this username already exists.";
        }
        handleError(error as AxiosError);
    }
};

watch(show, () => {
    form.username = "";
    form.full_name = "";
    form.password = "";
    form.confirm_password = "";
    form.disabled = false;
    form.is_admin = false;
});

onMounted(() => usernameInput.value?.focus());
</script>

<template>
    <NModal v-model:show="show">
        <NCard
            class="modal"
            title="Create a new user"
            :bordered="false"
            role="dialog"
            aria-modal="true"
        >
            <template #header-extra>
                <NIcon
                    :component="UserPlus"
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
                        label="Name"
                        path="username"
                        class="item"
                        content-class="item-content"
                        :validation-status="usernameError ? 'error' : undefined"
                        :feedback="usernameError"
                    >
                        <NInput
                            ref="username-input"
                            :value="form.username"
                            @update:value="onUsernameChange"
                            maxlength="64"
                            minlength="3"
                            placeholder="Enter username"
                        />
                    </NFormItem>

                    <NFormItem
                        label="Full name"
                        path="full_name"
                        class="item"
                    >
                        <NInput
                            v-model:value="form.full_name"
                            maxlength="128"
                            show-count
                            placeholder="Enter display name"
                        />
                    </NFormItem>
                    <NFormItem
                        label="Password"
                        path="password"
                        class="item"
                    >
                        <NInput
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
                    <NFormItem
                        label="Role"
                        class="item"
                        path="is_admin"
                    >
                        <NSelect
                            :options="[
                                { label: 'Administrator', value: 1 },
                                { label: 'Viewer', value: 0 },
                            ]"
                            @update:value="(v) => (form.is_admin = Boolean(v))"
                            :value="form.is_admin ? 1 : 0"
                        />
                    </NFormItem>
                    <NFormItem
                        label="Other options"
                        class="item"
                        path="disabled"
                    >
                        <NCheckbox v-model:checked="form.disabled"> Account disabled </NCheckbox>
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
