import ipaddress
import re

from app.models.exceptions import DNSValidationError
from app.models.record import SupportedDNSRecordTypes

FQDN_BASE_VALID_CHARACTERS = re.compile(r"(?:[a-z0-9_\-]+\.)+")
QUERY_VALID_CHARACTERS = re.compile(r"(?:[a-z0-9_\-\*\?]+\.)+")


def is_valid_ipv4(value: str) -> bool:
    try:
        return isinstance(ipaddress.ip_address(value), ipaddress.IPv4Address)
    except ValueError:
        return False


def is_valid_ipv6(value: str) -> bool:
    try:
        return isinstance(ipaddress.ip_address(value), ipaddress.IPv6Address)
    except ValueError:
        return False


def validate_dns_name(name: str):
    """
    Checks if name passed the characters validation and meets the octet-length constraints.
    """

    if not name:
        raise DNSValidationError("DNS name cannot be empty.")

    normalized_name = f"{name.rstrip('.').lower()}."

    if not FQDN_BASE_VALID_CHARACTERS.fullmatch(normalized_name):
        raise DNSValidationError("DNS name contains invalid characters.")

    labels = normalized_name.rstrip(".").split(".")

    if any(not label for label in labels):
        raise DNSValidationError("DNS name cannot contain empty labels.")

    for label in labels:
        if len(label.encode("utf-8")) > 63:
            raise DNSValidationError("DNS name labels cannot exceed 63 octets.")

    # one length octet per label + label contents + terminating zero octet
    wire_length = sum(len(label.encode("utf-8")) + 1 for label in labels) + 1

    if wire_length > 255:
        raise DNSValidationError("DNS name cannot exceed 255 octets.")


def is_record_name_in_zone(record_name: str, zone_name: str):
    """
    Determines whether the record belongs to a zone.
    """

    normalized_name = f"{record_name.rstrip('.').lower()}."
    normalized_zone = f"{zone_name.rstrip('.').lower()}."

    return normalized_name == normalized_zone or normalized_name.endswith(f".{normalized_zone}")


def validate_dns_record_name(name: str, zone_name: str):
    """
    Validates DNS name characters and length and ensures it belongs to the specified zone.
    """

    validate_dns_name(name)

    if not is_record_name_in_zone(name, zone_name):
        raise DNSValidationError("DNS record name is out of zone.")


def validate_a_record_content(content: str):
    """
    Validates the A record content.
    """
    if not is_valid_ipv4(content):
        raise DNSValidationError("Invalid A record content: An A record requires a valid IPv4 address.")


def validate_aaaa_record_content(content: str):
    """
    Validates the AAAA record content.
    """
    if not is_valid_ipv6(content):
        raise DNSValidationError("Invalid AAAA record content: An AAAA record requires a valid IPv6 address.")


def validate_cname_record_content(content: str):
    """
    Validates the CNAME record content.
    """
    try:
        validate_dns_name(content)
    except DNSValidationError as e:
        raise DNSValidationError(f"Invalid CNAME record content: {e}")


def validate_mx_record_content(content: str):
    """
    Validates the MX record content.
    """

    parts = content.split()

    if len(parts) != 2:
        raise DNSValidationError("MX record must contain preference and exchange.")

    preference, exchange = parts

    try:
        preference = int(preference)
    except ValueError:
        raise DNSValidationError("MX preference must be an integer.")

    if not 0 <= preference <= 65535:
        raise DNSValidationError("MX preference must be between 0 and 65535.")

    validate_dns_name(exchange)


def validate_srv_record_content(content: str):
    """
    Validates the SRV record content.
    """

    parts = content.split()

    if len(parts) != 4:
        raise DNSValidationError("SRV record must contain priority, weight, port, and target.")

    priority, weight, port, target = parts

    for field_name, value in (("priority", priority), ("weight", weight), ("port", port)):
        try:
            value = int(value)
        except ValueError:
            raise DNSValidationError(f"SRV {field_name} must be an integer.")

        if not 0 <= value <= 65535:
            raise DNSValidationError(f"SRV {field_name} must be between 0 and 65535.")

    validate_dns_name(target)


def validate_txt_record_content(content: str):
    """
    Validates the TXT record content.
    """

    if not content:
        return DNSValidationError("TXT record cannot be empty")
    i = 0

    while i < len(content):
        if content[i] != '"':
            return DNSValidationError(f'Expected " at position {i + 1}. Each TXT string must be enclosed in double quotes.')

        i += 1
        closed = False

        while i < len(content):
            char = content[i]

            if char == '"':
                i += 1
                closed = True
                break

            if char == "\\":
                if i + 1 >= len(content):
                    return DNSValidationError(f"Invalid escape at position {i + 1}. A backslash must be followed by a character.")

                i += 2
                continue

            i += 1

        if not closed:
            return DNSValidationError('Missing closing " for TXT string.')

        if i == len(content):
            return True

        if content[i] != " ":
            return DNSValidationError(f"TXT strings must be separated by exactly one space at position {i + 1}.")

        i += 1

        if i >= len(content):
            return DNSValidationError("Expected another TXT string after the separator.")

        if content[i] != '"':
            return DNSValidationError(f'Expected " after the separator at position {i + 1}.')

    return True


def validate_record_content(content: str, type_: SupportedDNSRecordTypes):
    """
    Raises an error if the provided content value is not valid.
    """

    match type_:
        case "A":
            validate_a_record_content(content)
        case "AAAA":
            validate_aaaa_record_content(content)
        case "CNAME":
            validate_cname_record_content(content)
        case "MX":
            validate_mx_record_content(content)
        case "SRV":
            validate_srv_record_content(content)
        case "TXT":
            validate_txt_record_content(content)


def validate_search_query(query: str):
    normalized_query = f"{query.rstrip('.')}."

    if not QUERY_VALID_CHARACTERS.fullmatch(normalized_query):
        raise DNSValidationError(
            "Invalid query. The query may only contain valid DNS record name characters and the supported wildcards '*' and '?'."
        )
