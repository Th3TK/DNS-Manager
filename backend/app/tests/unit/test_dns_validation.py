import pytest
from app.management.dns.validation import (
    DNSValidationError,
    validate_a_record_content,
    validate_aaaa_record_content,
    validate_cname_record_content,
    validate_dns_name,
    validate_dns_record_name,
    validate_mx_record_content,
    validate_record_content,
    validate_srv_record_content,
)
from app.models.record import SupportedDNSRecordTypes

# ---------------------------------------------------------------------------
# DNS names
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name",
    [
        "example.com",
        "example.com.",
        "www.example.com",
        "www.example.com.",
        "a.b.c",
        "foo-bar.example.com",
        "123.example.com",
        "example123.com",
    ],
)
def test_validate_dns_name_valid(name: str):
    validate_dns_name(name)


@pytest.mark.parametrize(
    "name",
    [
        "",
        ".",
        ".example.com",
        "example..com",
        "a" * 64 + ".com",
    ],
)
def test_validate_dns_name_invalid(name: str):
    with pytest.raises(DNSValidationError):
        validate_dns_name(name)


def test_validate_dns_name_maximum_label_length():
    validate_dns_name(("a" * 63) + ".com")


def test_validate_dns_name_label_over_maximum_length():
    with pytest.raises(DNSValidationError):
        validate_dns_name(("a" * 64) + ".com")


# ---------------------------------------------------------------------------
# DNS record names
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "zone_name"),
    [
        ("www.example.com", "example.com"),
        ("www.example.com.", "example.com."),
        ("example.com", "example.com"),
    ],
)
def test_validate_dns_record_name_valid(name: str, zone_name: str):
    validate_dns_record_name(name, zone_name)


@pytest.mark.parametrize(
    ("name", "zone_name"),
    [
        ("other.com", "example.com"),
        ("www.other.com", "example.com"),
        ("foo.example.com", "other.com"),
        ("", "example.com"),
        ("@", "example.com"),
        ("www..example.com", "example.com"),
    ],
)
def test_validate_dns_record_name_invalid(name: str, zone_name: str):
    with pytest.raises(DNSValidationError):
        validate_dns_record_name(name, zone_name)


# ---------------------------------------------------------------------------
# A records
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "content",
    [
        "0.0.0.0",
        "1.2.3.4",
        "127.0.0.1",
        "192.168.1.1",
        "255.255.255.255",
    ],
)
def test_validate_a_record_content_valid(content: str):
    validate_a_record_content(content)


@pytest.mark.parametrize(
    "content",
    [
        "",
        "1.2.3",
        "1.2.3.4.5",
        "256.1.1.1",
        "1.2.3.256",
        "1.1.1.1/24",
        "::1",
        "example.com",
    ],
)
def test_validate_a_record_content_invalid(content: str):
    with pytest.raises(DNSValidationError):
        validate_a_record_content(content)


# ---------------------------------------------------------------------------
# AAAA records
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "content",
    [
        "::",
        "::1",
        "2001:db8::1",
        "fe80::1",
        "2001:0db8:0000:0000:0000:0000:0000:0001",
        "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff",
    ],
)
def test_validate_aaaa_record_content_valid(content: str):
    validate_aaaa_record_content(content)


@pytest.mark.parametrize(
    "content",
    [
        "",
        "1.2.3.4",
        "2001:db8:::1",
        "2001:db8::1::2",
        "gggg::1",
        "2001:db8::1/64",
        "2001:db8::/128",
        "example.com",
    ],
)
def test_validate_aaaa_record_content_invalid(content: str):
    with pytest.raises(DNSValidationError):
        validate_aaaa_record_content(content)


# ---------------------------------------------------------------------------
# CNAME records
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "content",
    [
        "example.com",
        "example.com.",
        "www.example.com",
        "target.example.com.",
        "foo-bar.example.com",
    ],
)
def test_validate_cname_record_content_valid(content: str):
    validate_cname_record_content(content)


@pytest.mark.parametrize(
    "content",
    [
        "",
        ".",
        "example..com",
        ".example.com",
    ],
)
def test_validate_cname_record_content_invalid(content: str):
    with pytest.raises(DNSValidationError):
        validate_cname_record_content(content)


# ---------------------------------------------------------------------------
# MX records
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "content",
    [
        "10 mail.example.com",
        "10 mail.example.com.",
        "0 mail.example.com",
        "100 mx.example.org.",
    ],
)
def test_validate_mx_record_content_valid(content: str):
    validate_mx_record_content(content)


@pytest.mark.parametrize(
    "content",
    [
        "",
        "mail.example.com",
        "mail.example.com 10",
        "-1 mail.example.com",
        "65536 mail.example.com",
        "abc mail.example.com",
        "10",
        "10 mail..example.com",
        "10 " + 100 * "a" + ".com",
    ],
)
def test_validate_mx_record_content_invalid(content: str):
    with pytest.raises(DNSValidationError):
        validate_mx_record_content(content)


# ---------------------------------------------------------------------------
# SRV records
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "content",
    [
        "0 0 443 example.com",
        "10 20 443 server.example.com",
        "0 0 0 target.example.com.",
        "65535 65535 65535 server.example.com.",
    ],
)
def test_validate_srv_record_content_valid(content: str):
    validate_srv_record_content(content)


@pytest.mark.parametrize(
    "content",
    [
        "",
        "10 20 443",
        "10 20 server.example.com",
        "10 20 443 1234 server.example.com",
        "-1 20 443 server.example.com",
        "10 -1 443 server.example.com",
        "10 20 -1 server.example.com",
        "65536 20 443 server.example.com",
        "10 65536 443 server.example.com",
        "10 20 65536 server.example.com",
        "abc 20 443 server.example.com",
        "10 abc 443 server.example.com",
        "10 20 abc server.example.com",
        "10 20 443 server..example.com",
    ],
)
def test_validate_srv_record_content_invalid(content: str):
    with pytest.raises(DNSValidationError):
        validate_srv_record_content(content)


# ---------------------------------------------------------------------------
# Generic record content validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("type_", "content"),
    [
        ("A", "1.2.3.4"),
        ("AAAA", "2001:db8::1"),
        ("CNAME", "example.com."),
        ("MX", "10 mail.example.com."),
        ("SRV", "10 20 443 server.example.com."),
        ("TXT", "hello world"),
    ],
)
def test_validate_record_content_valid(type_: SupportedDNSRecordTypes, content: str):
    validate_record_content(content, type_)


@pytest.mark.parametrize(
    ("type_", "content"),
    [
        ("A", "2001:db8::1"),
        ("AAAA", "1.2.3.4"),
        ("CNAME", "example..com"),
        ("MX", "mail.example.com"),
        ("SRV", "10 20 443"),
    ],
)
def test_validate_record_content_invalid(type_: SupportedDNSRecordTypes, content: str):
    with pytest.raises(DNSValidationError):
        validate_record_content(content, type_)


@pytest.mark.parametrize(
    "type_",
    [
        "A",
        "AAAA",
        "CNAME",
        "TXT",
        "MX",
        "SRV",
    ],
)
def test_validate_record_content_accepts_supported_types(type_: SupportedDNSRecordTypes):
    valid_content = {
        "A": "1.2.3.4",
        "AAAA": "2001:db8::1",
        "CNAME": "example.com.",
        "TXT": "hello world",
        "MX": "10 mail.example.com.",
        "SRV": "10 20 443 server.example.com.",
    }

    validate_record_content(valid_content[type_], type_)
