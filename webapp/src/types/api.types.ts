export type RequestMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

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
