from app.dns.models.record import SupportedDNSRecordTypes
from app.dns.validators.base import DNSValidationError, is_valid_ipv4, is_valid_ipv6, validate_dns_name


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


def validate_record_content(content: str, type_: SupportedDNSRecordTypes):
    """
    Raises an error if the provided content value is not valid.

    Content of `TXT` records is not validated. `TXT` content validation should be handled by the DNS provider adapters
    to comply with the format requirements of the respective provider.
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
            pass
