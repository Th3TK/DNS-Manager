import type { AxiosError } from "axios";
import { sendRequest } from "./requests";

export const login = async (username: string, password: string, onError: (err: AxiosError) => void) =>
    await sendRequest(
        "POST",
        "/auth/login",
        {
            data: new URLSearchParams({ username, password }),
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
        },
        onError,
    );
