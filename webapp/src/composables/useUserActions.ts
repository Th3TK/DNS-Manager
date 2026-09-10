import { HttpStatusCode, type AxiosError } from "axios";
import type { User } from "../types/api.types";
import { useErrorHandler } from "./useErrorHandler";
import { ref } from "vue";
import { deleteUser, logout } from "../services/api";
import { useRouter } from "vue-router";
import { useAuthenticationStore } from "../stores/useAuthenticationStore";
import _ from "lodash";
import useBulkDelete from "./useBulkDelete.ts";

export const useUserActions = (onDeleteSuccess?: () => void, onDeleteError?: (error?: AxiosError) => void) => {
    const authentication = useAuthenticationStore();
    const { handleError } = useErrorHandler();
    const { onBulkDelete } = useBulkDelete();
    const router = useRouter();

    const changePasswordModalOpened = ref(false);
    const deleteModalOpened = ref(false);
    const createModalOpened = ref(false);
    const editModalOpened = ref(false);

    const onDelete = async (users: User | User[]) => {
        const isArray = _.isArray(users);

        if (isArray && users.length > 1) {
            const { failed } = await onBulkDelete<User>(users, (user: User) => deleteUser(user.username), "user", "username");

            if (!_.isEmpty(failed)) {
                return onDeleteError?.();
            }

            return onDeleteSuccess?.();
        }

        const user = isArray ? users[0] : users;

        deleteUser(user.username)
            .then(() => {
                onDeleteSuccess?.();
            })
            .catch((error: AxiosError) => {
                if (![HttpStatusCode.NotFound, HttpStatusCode.Conflict].includes(error.response?.status as HttpStatusCode)) {
                    handleError(error);
                }
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
