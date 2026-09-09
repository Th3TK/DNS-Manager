<script setup lang="ts">
import { NButton, NCard, NCheckbox, NFlex, NForm, NFormItem, NIcon, NInput, NModal, NSelect, type FormInst } from "naive-ui";
import type { ModifyUserForm, User } from "../../types/api.types";
import { onMounted, reactive, ref, useTemplateRef, watch } from "vue";
import { AxiosError, HttpStatusCode, isAxiosError } from "axios";
import { modifyUser } from "../../services/api";
import { useErrorHandler } from "../../composables/useErrorHandler";
import { User as UserIcon } from "@vicons/tabler";
import { useAuthenticationStore } from "../../stores/useAuthenticationStore";

const props = defineProps<{
    user: User;
    onSubmit?: (user: User) => void;
}>();

const authentication = useAuthenticationStore();

const { handleError } = useErrorHandler();

const show = defineModel<boolean>("show", { default: false });

const fullNameInput = useTemplateRef<InstanceType<typeof NInput>>("full-name-input");
const formRef = ref<FormInst | null>(null);

const form = reactive<ModifyUserForm>({
    full_name: props.user.full_name,
    disabled: props.user.disabled,
    is_admin: props.user.is_admin,
});

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
        const user = await modifyUser(props.user.username, form);

        close();

        if (authentication.user?.username === user.username) {
            authentication.refresh();
        }

        props.onSubmit?.(user);
    } catch (error) {
        if (isAxiosError(error) && error.response?.status === HttpStatusCode.Conflict) {
            handleError(error, "Action Not Allowed");
            return;
        }
        handleError(error as AxiosError);
    }
};

watch([show, () => props.user], () => {
    form.full_name = props.user.full_name;
    form.disabled = props.user.disabled;
    form.is_admin = props.user.is_admin;
});

onMounted(() => fullNameInput.value?.focus());
</script>

<template>
    <NModal
        v-model:show="show"
        class="modal"
    >
        <NCard
            class="modal-card"
            title="Edit user"
            :bordered="false"
            role="dialog"
            aria-modal="true"
        >
            <template #header-extra>
                <NIcon
                    :component="UserIcon"
                    size="24"
                />
            </template>
            <NForm
                ref="formRef"
                :model="form"
                @submit.prevent="onSubmit"
                class="form"
            >
                <NFlex
                    vertical
                    size="large"
                    class="stack"
                >
                    <NFormItem
                        label="Username"
                        class="item"
                        :show-feedback="false"
                    >
                        <NInput
                            :value="user.username"
                            disabled
                        />
                    </NFormItem>
                    <NFormItem
                        label="Full name"
                        path="full_name"
                        class="item"
                        :show-feedback="false"
                    >
                        <NInput
                            ref="full-name-input"
                            v-model:value="form.full_name"
                            maxlength="128"
                            show-count
                            placeholder="Enter display name"
                        />
                    </NFormItem>
                    <NFormItem
                        label="Role"
                        class="item"
                        path="is_admin"
                        :feedback="!form.is_admin ? 'You will no longer be able to manage user accounts.' : undefined"
                        :validation-status="!form.is_admin ? 'warning' : undefined"
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
                        :show-label="false"
                        class="item"
                        path="disabled"
                        :feedback="form.disabled ? 'Disabling this account will log you out immediately.' : undefined"
                        :validation-status="form.disabled ? 'warning' : undefined"
                    >
                        <NCheckbox
                            v-model:checked="form.disabled"
                            class="checkbox"
                            size="large"
                        >
                            Account disabled
                        </NCheckbox>
                    </NFormItem>

                    <NFlex class="controls">
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
.modal,
.modal-card {
    width: 500px;
    height: 450px;
    overflow: hidden;
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
:deep(.n-form-item-feedback-wrapper) {
    min-height: 0;
}

.stack {
    height: 100%;
}

.form {
    height: 100%;
}

.controls {
    margin-top: auto !important;
}
</style>
