import type { AxiosError } from "axios";
import type { DNSRecord, ChangeHistoryEntry, DNSZone, TrashEntry, User } from "../types/api.types";
import { sendRequest } from "./requests";
import type { DataPaginated, Filters } from "../types/table.types";
import _ from "lodash";

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

export const getUsers = async () => await sendRequest<User[]>("GET", "/users");

const prepareTableParams = <T = unknown>(
    page: number,
    pageSize: number,
    filters: Filters<T> = {},
    sortBy?: keyof DNSZone | null,
    sortOrder?: "ascend" | "descend" | null,
): URLSearchParams => {
    const params = new URLSearchParams({
        page: page.toString(),
        size: pageSize.toString(),
    });

    if (sortBy) params.append("sort_by", sortBy);
    if (sortOrder) params.append("sort_order", sortOrder);

    _.forEach(filters, (value, key) => {
        if (_.isEmpty(value)) return;

        _.forEach(_.castArray(value), (item) => params.append(key, String(item)));
    });

    return params;
};

export const getZones = async (): Promise<DNSZone[]> => await sendRequest<DNSZone[]>("GET", `/zones`);

export const getRecords = async (zoneName: string): Promise<DNSRecord[]> =>
    await sendRequest<DNSRecord[]>("GET", `/zones/${zoneName}/records`);

export const getChangeHistory = async (
    page: number,
    pageSize: number,
    filters: Filters<ChangeHistoryEntry>,
): Promise<DataPaginated<ChangeHistoryEntry>> => {
    const params = prepareTableParams(page, pageSize, filters);
    return await sendRequest<DataPaginated<ChangeHistoryEntry>>("GET", `/log?${params.toString()}`);
};

export const getAllChangeHistoryActors = async () => await sendRequest<string[]>("GET", "/log/actors");

export const getTrash = async (page: number, pageSize: number, filters: Filters<TrashEntry>): Promise<DataPaginated<TrashEntry>> => {
    const params = prepareTableParams(page, pageSize, filters);
    return await sendRequest<DataPaginated<TrashEntry>>("GET", `/trash?${params.toString()}`);
};
