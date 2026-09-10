import type { AxiosRequestConfig } from "axios";
import type { RequestMethod } from "../types/api.types";
import axios, { HttpStatusCode, isAxiosError } from "axios";
import _ from "lodash";
import { combinePaths } from "../utils/url";
import APP_CONFIG from "../config/app.config";

// const sendFetch = async () : Promise<AxiosResponse> => await axios({})

const BASE_REQUEST_CONFIG = {
    transitional: { clarifyTimeoutError: true },
    timeout: 10000,
    timeoutErrorMessage: "No response from the API service.",
    withCredentials: true,
};

export const sendRequest = async <T = any>(
    method: RequestMethod,
    path: string,
    config: AxiosRequestConfig = {},
    refreshTokensOnUnauthorized: boolean = true,
): Promise<T> => {
    const fullPath = combinePaths(APP_CONFIG.API_URL_HTTP, path);

    const getFullConfig = () => _.merge(config, BASE_REQUEST_CONFIG);

    const sendAxiosRequest = async () => await axios.request<T>({ ...getFullConfig(), method: method, url: fullPath });

    try {
        const response = await sendAxiosRequest();
        return response.data;
    } catch (error) {
        if (!isAxiosError(error)) {
            console.error("Unhandled error occured during fetch.");
            throw error;
        }

        if (error.response?.status === HttpStatusCode.Unauthorized && refreshTokensOnUnauthorized) {
            try {
                await axios.post(combinePaths(APP_CONFIG.API_URL_HTTP, "/auth/refresh"), undefined, BASE_REQUEST_CONFIG);
            } catch (refreshError) {
                if (isAxiosError(refreshError)) throw refreshError;

                console.error("Unhandled error occurred during token refresh.", refreshError);
            }

            return sendRequest(method, path, config, false);
        }

        if (!error.response && !error.request) {
            console.error("Unhandled axios error occured during fetch.");
        }
        throw error;
    }
};
