import _ from "lodash";
import ipaddr from "ipaddr.js";

export const sanitizeDnsName = (value: string) =>
    value
        .toLowerCase()
        .replace(/[^a-z0-9._-]/g, "")
        .replace(/\.{2,}/g, ".");

export const normalizeDnsName = (value: string) => {
    const sanitized = _.trimEnd(sanitizeDnsName(value), ".");

    return sanitized ? `${sanitized}.` : "";
};

export const normalizeDnsRecordName = (value: string, zoneName: string) => {
    const recordName = normalizeDnsName(value);
    return recordName.endsWith(zoneName) ? recordName : `${recordName}${zoneName}`;
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

export const sanitazeIpv4Address = (value: string) =>
    value
        .replace(/[^0-9.]/g, "")
        .split(".")
        .map((octet) => (_.parseInt(octet) > 255 ? "255" : octet))
        .slice(0, 4)
        .join(".");

export const sanitizeIpv6Address = (value: string): string => value.replace(/[^0-9a-fA-F:]/g, "").slice(0, 39);

export const sanitizeMxContent = (value: string) =>
    value
        .replace(/\s+/g, " ")
        .split(" ")
        .slice(0, 2)
        .map((e, i) => (i === 1 ? sanitizeDnsName(e) : e.replace(/[^\d]/g, "")))
        .join(" ");

export const normalizeMxContent = (value: string) =>
    // normalize exchange part of the content
    value
        ? sanitizeMxContent(value)
              .split(" ")
              .filter((e) => e)
              .map((e, i) => (i === 1 ? normalizeDnsName(e) : e))
              .join(" ")
        : "";

export const sanitizeSrvContent = (value: string) =>
    value
        .replace(/\s+/g, " ")
        .split(" ")
        .slice(0, 4)
        .map((e, i) => (i === 3 ? sanitizeDnsName(e) : e.replace(/[^\d]/g, "")))
        .join(" ");

export const normalizeSrvContent = (value: string) =>
    // normalize target part of the content
    value
        ? sanitizeSrvContent(value)
              .split(" ")
              .filter((e) => e)
              .map((e, i) => (i === 3 ? normalizeDnsName(e) : e))
              .join(" ")
        : "";

export const isValidDnsName = (value: string) => {
    if (!value) return;

    const normalized = `${_.trimEnd(value, ".")}.`;

    if (!/(?:[a-z0-9_-]+\.)+/g.test(normalized)) return false;

    const labels = _.trimEnd(normalized, ".").split(".");

    if (labels.some((e) => !e || e.length > 63)) return false;

    return normalized.length <= 255;
};

export const isValidIpv6Address = (value: string): boolean => ipaddr.IPv6.isValid(value);

export const isValidMxContent = (value: string) => {
    const parts = value.trim().split(/\s+/);

    if (parts.length != 2) return false;

    const [preference, exchange] = parts;

    // check if preference is a integer from range [0, 65535] inclusive
    if (!/^\d+$/.test(preference) || Number(preference) > 65535) return;

    return isValidDnsName(exchange);
};

export const isValidSrvContent = (value: string) => {
    const parts = value.trim().split(/\s+/);

    if (parts.length != 4) return false;

    const [priority, weight, port, target] = parts;

    // check if priority, weigth and port are integers from range [0, 65535] inclusive
    if ([priority, weight, port].some((e) => !/^\d+$/.test(e) || Number(e) > 65535)) return false;

    return isValidDnsName(target);
};
