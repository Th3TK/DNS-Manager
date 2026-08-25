import type { AxiosError } from "axios";
import type { User } from "../types/api.types";
import { sendRequest } from "./requests";

export const login = async (username: string, password: string) =>
    await sendRequest<true>(
        "POST",
        "/auth/login",
        {
            data: new URLSearchParams({ username, password }),
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
        },
        false,
    );

export const getLoggedInUser = async () => await sendRequest<User>("GET", "/users/me");

export const getAuthenticatedUser = async () => {
    try {
        return await getLoggedInUser();
    } catch {
        return null;
    }
};
