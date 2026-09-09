export const sanitizeUsername = (value: string) => value.toLowerCase().replace(/[^a-z0-9_@.+:$-]/g, "");
