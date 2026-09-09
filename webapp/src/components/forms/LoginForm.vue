<script setup lang="ts">
import { onMounted, reactive, ref, useTemplateRef } from "vue";
import { NForm, NFormItem, NInput, NButton, NSpace, NCard, NText, type FormInst, type FormRules } from "naive-ui";

import { useRouter } from "vue-router";
import { useNotification } from "naive-ui";
import { useErrorHandler } from "../../composables/useErrorHandler.ts";
import { HttpStatusCode } from "axios";
import { login } from "../../services/api.ts";
import { useRecordsStatusStore } from "../../stores/useRecordsStatusStore.ts";
import { useAuthenticationStore } from "../../stores/useAuthenticationStore.ts";

const notification = useNotification();
const errorHandler = useErrorHandler();

const authentication = useAuthenticationStore();
const recordsStatus = useRecordsStatusStore();
const router = useRouter();

const usernameInput = useTemplateRef<InstanceType<typeof NInput>>("username-input");
const formRef = useTemplateRef<FormInst>("form-ref");

const form = reactive({
    username: "",
    password: "",
});

const rules: FormRules = {
    username: {
        required: true,
        message: "Username is required",
        trigger: ["input", "blur"],
    },
    password: {
        required: true,
        message: "Password is required",
        trigger: ["input", "blur"],
    },
};

const onLogin = async () => {
    try {
        await formRef.value?.validate();
    } catch {
        return;
    }

    const success = await login(form.username, form.password).catch((error) => {
        if (error.response?.status === HttpStatusCode.Unauthorized) {
            notification.error({
                title: "Login failed",
                content: "Incorrect username or password.",
                duration: 3000,
            });
        } else errorHandler.handleError(error);

        return false;
    });

    if (!success) return;

    router.push({ name: "Dashboard" });
    recordsStatus.connect();
    authentication.refresh();
};

onMounted(() => usernameInput.value?.focus());
</script>

<template>
    <NCard class="form">
        <NText
            tag="h2"
            class="header"
        >
            Log in to your account
        </NText>

        <NForm
            ref="form-ref"
            :model="form"
            :rules="rules"
            @submit.prevent="onLogin"
        >
            <NFormItem
                label="Username"
                path="username"
            >
                <NInput
                    v-model:value="form.username"
                    placeholder="Username"
                />
            </NFormItem>

            <NFormItem
                label="Password"
                path="password"
            >
                <NInput
                    v-model:value="form.password"
                    type="password"
                    show-password-on="click"
                    placeholder="Password"
                />
            </NFormItem>

            <NSpace justify="end">
                <NButton
                    type="primary"
                    attr-type="submit"
                    class="submitButton"
                >
                    Log in
                </NButton>
            </NSpace>
        </NForm>
    </NCard>
</template>

<style scoped>
.form {
    width: 400px;
}
.header {
    padding-bottom: var(--spacing-xs);
}
.submitButton {
    width: 100px;
}
</style>
