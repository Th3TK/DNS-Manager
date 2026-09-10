import _ from "lodash";
import type { DisplayedRecordStatus } from "../types/api.types";

export const naturalCompare = (a: string, b: string) => a.localeCompare(b, undefined, { numeric: true });

export const compareNumbers = (a: number, b: number) => (a - b > 0 ? 1 : -1);

export const compareDates = (a: Date | undefined, b: Date | undefined): number => {
    if (!a) return b ? 1 : 0;
    if (!b) return -1;

    return a.getTime() - b.getTime();
};

const statusOrder: Record<DisplayedRecordStatus, number> = {
    OK: 0,
    ERROR: 1,
    WARNING: 2,
    DISABLED: 3,
};

export const compareStatus = (a: DisplayedRecordStatus, b: DisplayedRecordStatus): number => statusOrder[a] - statusOrder[b];
