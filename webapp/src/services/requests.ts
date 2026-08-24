import type { AxiosError, AxiosRequestConfig, AxiosResponse } from "axios";
import type { RequestMethod } from "../types/api.types";
import axios, { HttpStatusCode, isAxiosError } from "axios";
import _ from "lodash";

// const sendFetch = async () : Promise<AxiosResponse> => await axios({})

const API_URL = `http://${window.location.hostname}:9000/api`;

const BASE_REQUEST_CONFIG = {
    transitional: { clarifyTimeoutError: true },
    timeout: 5000,
    timeoutErrorMessage: "No response from the API service.",
    withCredentials: true,
};

const combinePaths = (...paths: string[]) => `${paths.map((p) => _.trim(p, "/")).join("/")}`;

export const sendRequest = async <T = any>(
    method: RequestMethod,
    path: string,
    config: AxiosRequestConfig = {},
    onError: (error: AxiosError) => void,
    refreshTokensOnUnathorized: boolean = true,
): Promise<T | void> => {
    const fullPath = combinePaths(API_URL, path);

    const getFullConfig = () => _.merge(config, BASE_REQUEST_CONFIG);

    const sendAxiosRequest = async () => await axios({ ...getFullConfig(), method: method, url: fullPath });

    try {
        const response = await sendAxiosRequest();
        return response.data;
    } catch (error) {
        if (!isAxiosError(error)) {
            console.error("Unhandled error occured during fetch.");
            throw error;
        }

        if (error.response?.status === HttpStatusCode.Unauthorized && refreshTokensOnUnathorized) {
            try {
                await axios.post(combinePaths(API_URL, "/auth/refresh"), undefined, BASE_REQUEST_CONFIG);
            } catch (refreshError) {
                if (isAxiosError(refreshError)) return onError(refreshError);

                console.error("Unhandled error occurred during token refresh.", refreshError);
            }

            return sendRequest(method, path, config, onError, false);
        }

        if (error.response || error.request) return onError(error);

        console.error("Unhandled axios error occured during fetch.");
        throw error;
    }
};
