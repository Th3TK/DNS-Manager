export type RequestMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

export interface User {
    username: string;
    full_name: string;
    is_admin: boolean;
    disabled: boolean;
}
