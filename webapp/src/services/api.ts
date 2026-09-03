import type { AxiosError } from "axios";
import type {
    DNSRecord,
    ChangeHistoryEntry,
    DNSZone,
    TrashEntry,
    User,
    CreateDNSZoneForm,
    CreateDNSRecordForm,
    ModifyDNSRecordForm,
} from "../types/api.types";
import { sendRequest } from "./requests";
import type { DataPaginated, Filters } from "../types/table.types";
import _ from "lodash";

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
                "Content-Type": "application/x-www-form-urlencoded",
            },
        },
        false,
    );

export const logout = () => sendRequest("POST", "/auth/logout");

/* ------------------------------------------------------------------------- */
/* USERS                                                                     */
/* ------------------------------------------------------------------------- */

export const getLoggedInUser = () => sendRequest<User>("GET", "/users/me");

export const getAuthenticatedUser = () => getLoggedInUser().catch(() => null);

export const getUsers = () => sendRequest<User[]>("GET", "/users");

export const getUser = (username: string) => sendRequest<User>("GET", `/user/${username}`);

/* ------------------------------------------------------------------------- */
/* DNS ZONES                                                                 */
/* ------------------------------------------------------------------------- */

export const getZones = () => sendRequest<DNSZone[]>("GET", "/zones");

export const getZone = (zoneName: string) => sendRequest<DNSZone>("GET", `/zones/${zoneName}`);

export const createZone = (form: CreateDNSZoneForm) => sendRequest<DNSZone>("POST", "/zones", { data: form });

export const deleteZone = (zoneName: string) => sendRequest<null>("DELETE", `/zones/${zoneName}`);

/* ------------------------------------------------------------------------- */
/* DNS RECORDS                                                               */
/* ------------------------------------------------------------------------- */

export const getRecords = (zoneName: string) => sendRequest<DNSRecord[]>("GET", `/zones/${zoneName}/records`);

export const getRecord = (zoneName: string, recordName: string, recordType: string) =>
    sendRequest<DNSRecord>("GET", `/zones/${zoneName}/records?record_name=${recordName}&record_type=${recordType}`);

export const createRecord = (zoneName: string, form: CreateDNSRecordForm) =>
    sendRequest<DNSRecord>("POST", `/zones/${zoneName}/record`, { data: form });

export const modifyRecord = (zoneName: string, form: ModifyDNSRecordForm) =>
    sendRequest<DNSRecord>("PATCH", `/zones/${zoneName}/record`, { data: form });

export const deleteRecord = (zoneName: string, recordName: string, recordType: string) =>
    sendRequest<null>("DELETE", `/zones/${zoneName}/record?record_name=${recordName}&record_type=${recordType}`);

/* ------------------------------------------------------------------------- */
/* CHANGE HISTORY                                                            */
/* ------------------------------------------------------------------------- */

export const getChangeHistory = async (
    page: number,
    pageSize: number,
    filters: Filters<ChangeHistoryEntry>,
): Promise<DataPaginated<ChangeHistoryEntry>> => {
    const params = prepareTableParams(page, pageSize, filters);
    return await sendRequest<DataPaginated<ChangeHistoryEntry>>("GET", `/log?${params.toString()}`);
};

/* ------------------------------------------------------------------------- */
/* TRASH                                                                     */
/* ------------------------------------------------------------------------- */

export const getTrash = (page: number, pageSize: number, filters: Filters<TrashEntry>) => {
    const params = prepareTableParams(page, pageSize, filters);
    return sendRequest<DataPaginated<TrashEntry>>("GET", `/trash?${params.toString()}`);
};

export const getTrashEntry = (uuid: string) => sendRequest<TrashEntry>("GET", `/trash/${uuid}`);
