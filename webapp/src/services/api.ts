import type {
    DNSRecord,
    ChangeHistoryEntry,
    DNSZone,
    TrashEntry,
    User,
    CreateDNSZoneForm,
    CreateDNSRecordForm,
    ModifyDNSRecordForm,
    CreateUserForm,
    NameSearchDNSRecord,
    ModifyUserForm,
    ChangePasswordForm,
} from "../types/api.types";
import { sendRequest } from "./requests";
import type { DataPaginated, FilterConfig, Filters } from "../types/table.types";
import _ from "lodash";
import { convertFiltersToParams } from "../utils/filters";

export const prepareTableParams = <T extends Record<string, any>>(
    page: number,
    pageSize: number,
    filters: Filters<T> = {},
    filterConfig: FilterConfig<T>,
    sortBy?: keyof T | null,
    sortOrder?: "ascend" | "descend" | null,
): URLSearchParams => {
    const params = new URLSearchParams({
        ...Object.fromEntries(convertFiltersToParams(filters, filterConfig).entries()),
        page: page.toString(),
        size: pageSize.toString(),
    });

    if (sortBy) params.append("sort_by", String(sortBy));
    if (sortOrder) params.append("sort_order", sortOrder);

    return params;
};

/* ------------------------------------------------------------------------- */
/* AUTHENTICATION                                                            */
/* ------------------------------------------------------------------------- */

export const login = (username: string, password: string) =>
    sendRequest<true>(
        "POST",
        "/auth/login",
        {
            data: new URLSearchParams({ username, password }),
            headers: {
                "Content-": "application/x-www-form-urlencoded",
            },
        },
        false,
    );

export const logout = () => sendRequest("POST", "/auth/logout");

export const refreshTokens = () => sendRequest("POST", "/auth/refresh", undefined, false);

/* ------------------------------------------------------------------------- */
/* USERS                                                                     */
/* ------------------------------------------------------------------------- */

export const getLoggedInUser = () => sendRequest<User>("GET", "/users/me");

export const getAuthenticatedUser = () => getLoggedInUser().catch(() => null);

export const getUsers = () => sendRequest<User[]>("GET", "/users");

export const getUser = (username: string) => sendRequest<User>("GET", `/users/${username}`);

export const createUser = (form: CreateUserForm) => sendRequest<User>("POST", "/users", { data: form });

export const modifyUser = (username: string, form: ModifyUserForm) => sendRequest<User>("PATCH", `/users/${username}`, { data: form });

export const deleteUser = (username: string) => sendRequest<null>("DELETE", `/users/${username}`);

export const changeOwnPassword = (form: ChangePasswordForm) => sendRequest<null>("PATCH", `/users/me/change-password`, { data: form });

export const changeUserPassword = (username: string, form: ChangePasswordForm) =>
    sendRequest<null>("PATCH", `/users/${username}/change-password`, { data: form });

/* ------------------------------------------------------------------------- */
/* DNS ZONES                                                                 */
/* ------------------------------------------------------------------------- */

export const getZones = (skipRecordCount: boolean = false, abortSignal: AbortSignal) =>
    sendRequest<DNSZone[]>("GET", `/zones?skip_record_count=${skipRecordCount}`, undefined, undefined, abortSignal);

export const getZone = (zoneName: string) => sendRequest<DNSZone>("GET", `/zones/${zoneName}`);

export const createZone = (form: CreateDNSZoneForm) => sendRequest<DNSZone>("POST", "/zones", { data: form });

export const deleteZone = (zoneName: string) => sendRequest<null>("DELETE", `/zones/${zoneName}`);

export const nameSearch = (query: string) => sendRequest<NameSearchDNSRecord[]>("GET", `/name-search?query=${query}`);

/* ------------------------------------------------------------------------- */
/* DNS RECORDS                                                               */
/* ------------------------------------------------------------------------- */

export const getAllRecords = () => sendRequest<DNSRecord[]>("GET", `/all-records`);

export const getRecords = (zoneName: string) => sendRequest<DNSRecord[]>("GET", `/zones/${zoneName}/records`);

export const getRecord = (zoneName: string, recordName: string, recordType: string) =>
    sendRequest<DNSRecord>("GET", `/zones/${zoneName}/record?record_name=${recordName}&record_type=${recordType}`);

export const createRecord = (zoneName: string, form: CreateDNSRecordForm) =>
    sendRequest<DNSRecord>("POST", `/zones/${zoneName}/record`, { data: form });

export const modifyRecord = (zoneName: string, recordName: string, recordType: string, form: ModifyDNSRecordForm) =>
    sendRequest<DNSRecord>("PATCH", `/zones/${zoneName}/record?record_name=${recordName}&record_type=${recordType}`, { data: form });

export const deleteRecord = (zoneName: string, recordName: string, recordType: string) =>
    sendRequest<null>("DELETE", `/zones/${zoneName}/record?record_name=${recordName}&record_type=${recordType}`);

/* ------------------------------------------------------------------------- */
/* CHANGE HISTORY                                                            */
/* ------------------------------------------------------------------------- */

export const getChangeHistory = async (
    page: number,
    pageSize: number,
    filters: Filters<ChangeHistoryEntry>,
    filterConfig: FilterConfig<ChangeHistoryEntry>,
): Promise<DataPaginated<ChangeHistoryEntry>> => {
    const params = prepareTableParams(page, pageSize, filters, filterConfig);
    return await sendRequest<DataPaginated<ChangeHistoryEntry>>("GET", `/log?${params.toString()}`);
};

/* ------------------------------------------------------------------------- */
/* TRASH                                                                     */
/* ------------------------------------------------------------------------- */

export const getTrash = (
    page: number,
    pageSize: number,
    filters: Filters<TrashEntry>,
    filterConfig: FilterConfig<ChangeHistoryEntry>,
    sortBy: keyof TrashEntry | null,
    sortOrder: "ascend" | "descend" | null,
) => {
    const params = prepareTableParams<TrashEntry>(page, pageSize, filters, filterConfig, sortBy, sortOrder);
    return sendRequest<DataPaginated<TrashEntry>>("GET", `/trash?${params.toString()}`);
};

export const getTrashEntry = (uuid: string) => sendRequest<TrashEntry>("GET", `/trash/${uuid}`);

export const restoreTrashEntry = (uuid: string) => sendRequest<TrashEntry>("POST", `/trash/restore/${uuid}`);

export const deleteTrashEntry = (uuid: string) => sendRequest<null>("DELETE", `/trash/permanently-delete/${uuid}`);
