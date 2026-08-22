from uuid import uuid4

import pytest
from app.models.record import DNSRecordProperties
from app.models.zone import DNSZoneProperties
from app.providers.base import DNSProvider
from fastapi import HTTPException


# test if health check correctly returns None
def test_health_check(provider: DNSProvider):
    assert provider.health_check() is None


def test_get_nonexistent_zone(provider: DNSProvider):
    zone_name = f"{uuid4().hex}.test.dev."

    assert provider.get_zone(zone_name) is None


def test_create_zone(provider: DNSProvider):
    zone_name = f"{uuid4().hex}.test.dev."

    try:
        zone = provider.create_zone(zone_name)

        assert isinstance(zone, DNSZoneProperties)
        assert zone.name == zone_name
    finally:
        provider.delete_zone(zone_name)


def test_get_zone(provider: DNSProvider, test_zone: str):
    zone = provider.get_zone(test_zone)

    assert zone is not None
    assert isinstance(zone, DNSZoneProperties)
    assert zone.name == test_zone


def test_get_zones(provider: DNSProvider, test_zone: str):
    zones = provider.get_zones()

    assert isinstance(zones, list)
    assert all(isinstance(zone, DNSZoneProperties) for zone in zones)
    assert any(zone.name == test_zone for zone in zones)


def test_delete_zone(provider: DNSProvider):
    zone_name = f"{uuid4().hex}.test.dev."

    provider.create_zone(zone_name)
    provider.delete_zone(zone_name)

    assert provider.get_zone(zone_name) is None


def test_get_nonexistent_record(
    provider: DNSProvider,
    test_zone: str,
):
    record = provider.get_record(
        test_zone,
        f"nonexistent.{test_zone}",
        "A",
    )

    assert record is None


def test_get_records_empty_zone(
    provider: DNSProvider,
    test_zone: str,
):
    records = provider.get_records(test_zone)

    assert records is not None

    assert not any(record.type in {"A", "AAAA", "CNAME", "TXT", "MX", "SRV"} for record in records)


def test_get_records_nonexistent_zone(provider: DNSProvider):
    zone_name = f"{uuid4().hex}.test.dev."

    assert provider.get_records(zone_name) is None


def test_create_record(provider: DNSProvider, test_zone: str):
    record_name = f"www.{test_zone}"

    record = provider.create_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    assert isinstance(record, DNSRecordProperties)
    assert record.name == record_name
    assert record.type == "A"
    assert record.content == "192.0.2.1"
    assert record.ttl == 300


def test_get_record(provider: DNSProvider, test_zone: str):
    record_name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    record = provider.get_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
    )

    assert record is not None
    assert isinstance(record, DNSRecordProperties)
    assert record.name == record_name
    assert record.type == "A"
    assert record.content == "192.0.2.1"
    assert record.ttl == 300


def test_get_records(provider: DNSProvider, test_zone: str):
    record_name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    records = provider.get_records(test_zone)

    assert records is not None

    matching_records = [record for record in records if record.name == record_name and record.type == "A"]

    assert len(matching_records) == 1

    record = matching_records[0]

    assert record.content == "192.0.2.1"
    assert record.ttl == 300


def test_modify_record(provider: DNSProvider, test_zone: str):
    record_name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    modified = provider.modify_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        content="192.0.2.2",
        ttl=600,
    )

    assert isinstance(modified, DNSRecordProperties)
    assert modified.name == record_name
    assert modified.type == "A"
    assert modified.content == "192.0.2.2"
    assert modified.ttl == 600

    retrieved = provider.get_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
    )

    assert retrieved is not None
    assert retrieved.content == "192.0.2.2"
    assert retrieved.ttl == 600


def test_delete_record(provider: DNSProvider, test_zone: str):
    record_name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    provider.delete_record(
        zone_name=test_zone,
        name=record_name,
        type_="A",
    )

    assert (
        provider.get_record(
            zone_name=test_zone,
            name=record_name,
            type_="A",
        )
        is None
    )


@pytest.mark.parametrize(
    "zone_name",
    [
        "test-zone.example.",
        "-test.example.",
        "test-.example.",
        "test_zone.example.",
        "_test.example.",
        "test_.example.",
        "test.-zone.example.",
        "test._zone.example.",
        "test.zone-_example.example.",
    ],
)
def test_create_zone_dns_name_characters(
    provider: DNSProvider,
    zone_name: str,
):
    try:
        zone = provider.create_zone(zone_name)
        assert zone.name == zone_name
    except HTTPException as exc:
        assert exc.status_code in (400, 422)
    else:
        provider.delete_zone(zone_name)


@pytest.mark.parametrize(
    "record_name",
    [
        "test-zone",
        "-test",
        "test-",
        "test_zone",
        "_test",
        "test_",
        "test-zone_name",
        "-test_zone-",
    ],
)
def test_create_record_dns_name_characters(
    provider: DNSProvider,
    test_zone: str,
    record_name: str,
):
    try:
        record = provider.create_record(
            zone_name=test_zone,
            name=f"{record_name}.{test_zone}",
            type_="A",
            content="192.0.2.1",
            ttl=300,
        )

        assert record.name == f"{record_name}.{test_zone}"

    except HTTPException as exc:
        assert exc.status_code in (400, 422)
