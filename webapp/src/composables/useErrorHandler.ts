import { HttpStatusCode, type AxiosError } from "axios";
import { useNotification } from "naive-ui";
import { AXIOS_ERROR_NOTIFICATIONS, DEFAULT_ERROR_NOTIFICATION, HTTP_ERROR_NOTIFICATIONS } from "../assets/notifications";
import _ from "lodash";
import { useRouter } from "vue-router";

type ErrorResponse = {
    detail: string;
};

export const useErrorHandler = () => {
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

    const handleError = (error: AxiosError, title?: string, message?: string) => {
        const httpErrorDetails = getHttpErrorDetails(error);
        const axiosErrorDetails = getAxiosErrorDetails(error);

        let notificationConfig = httpErrorDetails ?? axiosErrorDetails;

        if (_.isUndefined(notificationConfig)) {
            console.error("Unhandled error occured.", error);
            notificationConfig = DEFAULT_ERROR_NOTIFICATION;
        }

        notification.error({
            title: title ?? notificationConfig.title,
            content: message ?? notificationConfig.message,
            duration: 10000,
        });

        if (error?.response?.status === HttpStatusCode.Unauthorized) {
            router.push("/login");
        }
    };

    return { handleError };
};
