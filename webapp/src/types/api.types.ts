export type RequestMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

export interface User {
    username: string;
    full_name: string;
    is_admin: boolean;
    disabled: boolean;
}

export interface Zone {
    name: string;
    comment: string;
    author: string;
    origin: "manual" | "external";
}

export interface Record {
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
