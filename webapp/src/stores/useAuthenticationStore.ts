import { defineStore } from "pinia";
import { computed, ref } from "vue";
import type { User } from "../types/api.types";
import { getAuthenticatedUser } from "../services/api";
import { HttpStatusCode, type AxiosError } from "axios";

export const useAuthenticationStore = defineStore("authentication", () => {
    const user = ref<null | User>(null);
    const initialized = ref(false);

    const isAdmin = computed(() => user.value?.is_admin);

    const refresh = () =>
        getAuthenticatedUser()
            .then((response) => {
                user.value = response;
            })
            .catch((error: AxiosError) => {
                if (error.response?.status === HttpStatusCode.Unauthorized) {
                    user.value = null;
                    return;
                }
                console.error("Unhandled error occured while refreshing the authentication store:", error);
            })
            .finally(() => {
                initialized.value = true;
            });

    return {
        user,
        initialized,
        isAdmin,
        refresh,
    };
});
