import _ from "lodash";

export const sanitizeDnsName = (value: string) =>
    value
        .toLowerCase()
        .replace(/[^a-z0-9._-]/g, "")
        .replace(/\.{2,}/g, ".");

export const normalizeDnsName = (value: string) => {
    const sanitized = _.trimEnd(sanitizeDnsName(value), ".");

    return sanitized ? `${sanitized}.` : "";
};

export const isValidDnsZoneNameLength = (value: string): boolean => {
    const name = _.trimEnd(value, ".");

    // Maximum 63 octets per label
    if (name.split(".").some((label) => label.length > 63)) {
        return false;
    }

    // Maximum 253 characters for an ASCII FQDN
    return `${name}.`.length <= 253;
};
