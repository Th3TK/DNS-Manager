import ipaddress


class DNSValidationError(ValueError):
    pass


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
    Validates the DNS name's octet-length constraints only.
    It does not perform character validation.

    Character validation should be handled by the DNS provider adapters
    to comply with the format requirements of the respective provider.
    """

    if not name:
        raise DNSValidationError("DNS name cannot be empty.")

    labels = name.rstrip(".").split(".")

    if any(not label for label in labels):
        raise DNSValidationError("DNS name cannot contain empty labels.")

    for label in labels:
        if len(label.encode("utf-8")) > 63:
            raise DNSValidationError("DNS name labels cannot exceed 63 octets.")

    # one length octet per label + label contents + terminating zero octet
    wire_length = sum(len(label.encode("utf-8")) + 1 for label in labels) + 1

    if wire_length > 255:
        raise DNSValidationError("DNS name cannot exceed 255 octets.")


def validate_dns_record_name(name: str, zone_name: str):
    """
    Validates that the DNS record name satisfies DNS octet-length limits
    and belongs to the specified zone.
    """

    validate_dns_name(name)

    normalized_name = name.rstrip(".").lower()
    normalized_zone = zone_name.rstrip(".").lower()

    if normalized_name != normalized_zone and not normalized_name.endswith(f".{normalized_zone}"):
        raise DNSValidationError("DNS record name is out of zone.")
