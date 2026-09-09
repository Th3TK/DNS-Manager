import { HttpStatusCode, type AxiosError } from "axios";
import type { User } from "../types/api.types";
import { useErrorHandler } from "./useErrorHandler";
import { ref, type Ref } from "vue";
import { deleteUser, logout } from "../services/api";
import { useRouter } from "vue-router";
import { useAuthenticationStore } from "../stores/useAuthenticationStore";

export const useUserActions = (users: Ref<User | User[]>, onDeleteSuccess?: () => void, onDeleteError?: (error: AxiosError) => void) => {
    const authentication = useAuthenticationStore();
    const { handleError } = useErrorHandler();
    const router = useRouter();

    const changePasswordModalOpened = ref(false);
    const deleteModalOpened = ref(false);
    const createModalOpened = ref(false);
    const editModalOpened = ref(false);

    const onDelete = () => {
        Promise.all([users.value].flat().map((u) => deleteUser(u.username)))
            .then(onDeleteSuccess)
            .catch((error: AxiosError) => {
                // skip default error handling for 401 and 409
                if (![HttpStatusCode.NotFound, HttpStatusCode.Conflict].includes(error.response?.status as HttpStatusCode)) {
                    handleError(error);
                }

                // erorr handling for 409
                if (error.response?.status === HttpStatusCode.Conflict) {
                    handleError(error, "Action Not Allowed");
                }

                onDeleteError?.(error);
            });
    };

    const onLogout = async () => {
        await logout();
        router.push("/login");
        authentication.refresh();
    };

    return {
        changePasswordModalOpened,
        deleteModalOpened,
        createModalOpened,
        editModalOpened,
        onDelete,
        onLogout,
    };
};
