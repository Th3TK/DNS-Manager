export type RequestMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

export type SupportedDNSRecordTypes = "A" | "AAAA" | "CNAME" | "TXT" | "MX" | "SRV";
export interface User {
    username: string;
    full_name: string;
    is_admin: boolean;
    disabled: boolean;
}

export interface DNSZone {
    name: string;
    comment: string;
    author: string;
    origin: "manual" | "external";
    record_count: number;
}

export interface CreateDNSZoneForm {
    name: string;
    comment: string;
}

export interface DNSRecord {
    zone_name: string;
    name: string;
    type: string;
    content: string | string[];
    ttl: number;
    origin: "manual" | "external" | "automatic => traefik";
    author: string;
    comment: string;
    checks_enabled: boolean;
}

export interface CreateDNSRecordForm {
    name: string;
    type: SupportedDNSRecordTypes;
    content: string;
    ttl: number;
    comment: string | null;
    checks_enabled: boolean;
}

export interface ChangeHistoryEntry {
    entry_uuid: string;
    action_timestamp: string;
    actor_type: "user" | "watcher" | "automatic";
    actor: string;
    action: "created" | "changed" | "deleted" | "restored" | "permanently_deleted";
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
          object_data: CreateDNSZoneForm;
      }
    | {
          entry_uuid: string;
          deletion_timestamp: string;
          actor: string;
          object_type: "record";
          object_data: CreateDNSRecordForm;
      };
