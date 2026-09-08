import { HttpStatusCode, type AxiosError } from "axios";
import { useNotification } from "naive-ui";
import { AXIOS_ERROR_NOTIFICATIONS, DEFAULT_ERROR_NOTIFICATION, HTTP_ERROR_NOTIFICATIONS } from "../assets/notifications";
import _ from "lodash";
import { useRouter } from "vue-router";
import { useAuthenticationStore } from "../stores/useAuthenticationStore";
import { logout } from "../services/api";

type ErrorResponse = {
    detail: string;
};

export const useErrorHandler = () => {
    const authentication = useAuthenticationStore();
    const notification = useNotification();
    const router = useRouter();

    const getHttpErrorDetails = (error: AxiosError) => {
        const isHttpError = _.includes(["ERR_BAD_RESPONSE", "ERR_BAD_REQUEST"], error.code) && !_.isUndefined(error.response);

        if (!isHttpError) return;

        const detail = (error.response?.data as ErrorResponse).detail;
        const baseConfig = HTTP_ERROR_NOTIFICATIONS[error.response!.status];

        return _.merge(baseConfig, { message: detail });
    };

    const getAxiosErrorDetails = (error: AxiosError) => {
        const hasErrorCode = !_.isUndefined(error.code);

        if (!hasErrorCode) return;

        return AXIOS_ERROR_NOTIFICATIONS[error.code!];
    };

    const displayErrorNotification = (title: string, message: string) => {
        notification.error({
            title: title,
            content: message,
            duration: 10000,
        });
    };

    const handleUnauthorized = () => {
        router.push("/login");
        logout();

        displayErrorNotification(
            authentication.initialized ? "Session Expired" : "Unauthorized",
            authentication.initialized ? "Log in again to continue." : "Log in to continue.",
        );

        authentication.refresh();
    };

    const handleForbidden = () => {
        displayErrorNotification("Forbidden", "You do not have permission to perform this action.");
        authentication.refresh();
    };

    const handleError = (error: AxiosError, title?: string, message?: string) => {
        if (error.response?.status === HttpStatusCode.Unauthorized) {
            return handleUnauthorized();
        }
        if (error.response?.status === HttpStatusCode.Forbidden) {
            return handleForbidden();
        }

        const httpErrorDetails = getHttpErrorDetails(error);
        const axiosErrorDetails = getAxiosErrorDetails(error);

        let notificationConfig = httpErrorDetails ?? axiosErrorDetails;

        if (_.isUndefined(notificationConfig)) {
            console.error("Unhandled error occured.", error);
            notificationConfig = DEFAULT_ERROR_NOTIFICATION;
        }

        displayErrorNotification(title ?? notificationConfig.title, message ?? notificationConfig.message);
    };

    return { handleError, displayErrorNotification, handleUnauthorized, handleForbidden };
};
