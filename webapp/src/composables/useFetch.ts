import type { AxiosError, AxiosRequestConfig } from "axios";
import { ref, toValue, watch, type MaybeRefOrGetter } from "vue";
import { sendRequest } from "../services/requests";

const useFetch = <T = unknown>(path: MaybeRefOrGetter<string>, config: AxiosRequestConfig = {}) => {
    const data = ref<T | null>(null);
    const error = ref<AxiosError | null>(null);
    const loading = ref(true);

    const refresh = async () => {
        loading.value = true;
        error.value = null;

        await sendRequest<T>("GET", toValue(path), config)
            .then((json) => {
                data.value = json;
                error.value = null;
            })
            .catch((err) => {
                data.value = null;
                error.value = err;
            });

        loading.value = false;
    };

    watch([() => toValue(path), () => config], refresh, { immediate: true });

    return {
        data,
        error,
        loading,
        refresh,
    };
};

export default useFetch;
