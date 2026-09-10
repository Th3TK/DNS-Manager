export type RequestMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

export type SupportedDNSRecordTypes = "A" | "AAAA" | "CNAME" | "TXT" | "MX" | "SRV";
export interface User {
    username: string;
    full_name: string;
    is_admin: boolean;
    disabled: boolean;
}

export interface CreateUserForm {
    username: string;
    password: string;
    full_name: string;
    is_admin: boolean;
    disabled: boolean;
}
export interface ModifyUserForm {
    full_name: string;
    is_admin: boolean;
    disabled: boolean;
}

export interface ChangePasswordForm {
    password: string;
}

export type ResolutionStatus = "OK" | "MISMATCH" | "NO_RESOLUTION";

export type ReachabilityStatus = "REACHABLE" | "UNREACHABLE" | "NOT_CHECKED";

export interface APIRecordStatus {
    resolution: ResolutionStatus;
    reachability: ReachabilityStatus;
}

export type APIRecordStatuses = Record<string, Record<string, Record<string, APIRecordStatus | null>>>;

export interface APIRecordStatusCheckData {
    statuses: APIRecordStatuses | null;
    timestamp: string;
    next_check: string;
}

export type DisplayedRecordStatus = "OK" | "WARNING" | "ERROR" | "DISABLED";

export interface RecordStatusCheckData {
    statuses: APIRecordStatuses | null;
    timestamp: Date;
    next_check: Date;
    counts: Record<DisplayedRecordStatus, number>;
}

export interface DNSZone {
    name: string;
    comment: string | null;
    author: string;
    record_count: number;
}

export interface CreateDNSZoneForm {
    name: string;
    comment: string;
}

export interface RestoreDNSZoneForm {
    name: string;
    comment: string | null;
}

export type DNSRecordOrigin = "manual" | "external" | "automatic => traefik";

export interface DNSRecord {
    zone_name: string;
    name: string;
    type: string;
    content: string | string[];
    ttl: number;
    origin: DNSRecordOrigin;
    author: string;
    comment: string | null;
    checks_enabled: boolean;
}

export interface DNSRecordExtended extends DNSRecord {
    api_status: APIRecordStatus | null;
    displayed_status: DisplayedRecordStatus;
    status_timestamp: Date | undefined;
}

export interface CreateDNSRecordForm {
    name: string;
    type: SupportedDNSRecordTypes;
    content: string;
    ttl: number;
    comment: string | null;
    checks_enabled: boolean;
}

export interface RestoreDNSRecordForm {
    zone_name: string;
    name: string;
    type: SupportedDNSRecordTypes;
    content: string;
    ttl: number;
    comment: string | null;
    checks_enabled: boolean;
}

export interface ModifyDNSRecordForm {
    name: string | null;
    type: SupportedDNSRecordTypes | null;
    content: string | null;
    ttl: number | null;
    comment: string | null;
    checks_enabled: boolean | null;
}

export interface NameSearchDNSRecord {
    zone_name: string;
    name: string;
    type: string;
    content: string | string[];
    origin: DNSRecordOrigin;
    location: "active" | "trash";
    trash_entry_uuid: string | null;
}

export type ChangeHistoryAction = "created" | "changed" | "deleted" | "restored" | "permanently_deleted";

export interface ChangeHistoryEntry {
    entry_uuid: string;
    action_timestamp: string;
    actor_type: "user" | "watcher" | "automatic";
    actor: string;
    action: ChangeHistoryAction;
    affected_object_type: "zone" | "record";
    affected_object_name: string;
    object_before: Record<string, any> | null;
    object_after: Record<string, any> | null;
}

export type TrashEntry =
    | {
          entry_uuid: string;
          deletion_timestamp: string;
          actor: string;
          object_type: "zone";
          object_data: RestoreDNSZoneForm;
      }
    | {
          entry_uuid: string;
          deletion_timestamp: string;
          actor: string;
          object_type: "record";
          object_data: RestoreDNSRecordForm;
      };
