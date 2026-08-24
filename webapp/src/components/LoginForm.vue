<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from "vue";
import { NForm, NFormItem, NInput, NButton, NSpace, NCard, NText } from "naive-ui";
import { login } from "../services/api.ts";
import { useRouter } from "vue-router";

const router = useRouter();

const usernameInput = useTemplateRef<InstanceType<typeof NInput>>("username-input");

const username = ref("");
const password = ref("");

const onLogin = () => {
    login(username.value, password.value, (e) => console.log(e));
    // router.push("/");
};

onMounted(() => usernameInput.value?.focus());
</script>

<template>
    <NCard class="form">
        <NText
            tag="h2"
            class="header"
            >Log in to your account</NText
        >
        <NForm>
            <NFormItem
                label="Username"
                path="username"
            >
                <NInput
                    v-model:value="username"
                    placeholder="Username"
                    ref="username-input"
                />
            </NFormItem>

            <NFormItem
                label="Password"
                path="password"
            >
                <NInput
                    v-model:value="password"
                    type="password"
                    show-password-on="click"
                    placeholder="Password"
                />
            </NFormItem>

            <NSpace justify="end">
                <NButton
                    type="primary"
                    @click="onLogin"
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
