from uuid import uuid4

from app.providers.base import DNSProvider


def test_get_records_by_name(provider: DNSProvider, test_zone: str):
    name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )
    provider.create_record(
        zone_name=test_zone,
        name=name,
        type_="AAAA",
        content="2001:db8::1",
        ttl=600,
    )
    provider.create_record(
        zone_name=test_zone,
        name=f"api.{test_zone}",
        type_="A",
        content="192.0.2.2",
        ttl=300,
    )

    records = provider.get_records_by_name(
        zone_name=test_zone,
        name=name,
    )

    assert records is not None
    assert len(records) == 2

    assert {(record.name, record.type, record.content, record.ttl) for record in records} == {
        (name, "A", "192.0.2.1", 300),
        (name, "AAAA", "2001:db8::1", 600),
    }


def test_get_records_by_name_no_matching_records(
    provider: DNSProvider,
    test_zone: str,
):
    provider.create_record(
        zone_name=test_zone,
        name=f"www.{test_zone}",
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    records = provider.get_records_by_name(
        zone_name=test_zone,
        name=f"api.{test_zone}",
    )

    assert records == []


def test_get_records_by_name_nonexistent_zone(
    provider: DNSProvider,
):
    records = provider.get_records_by_name(
        zone_name=f"{uuid4().hex}.test.dev.",
        name=f"{uuid4().hex}.test.dev.",
    )

    assert records is None


def test_get_records_by_name_single_record(
    provider: DNSProvider,
    test_zone: str,
):
    name = f"www.{test_zone}"

    provider.create_record(
        zone_name=test_zone,
        name=name,
        type_="A",
        content="192.0.2.1",
        ttl=300,
    )

    records = provider.get_records_by_name(
        zone_name=test_zone,
        name=name,
    )

    assert records is not None
    assert len(records) == 1

    record = records[0]
    assert record.name == name
    assert record.type == "A"
    assert record.content == "192.0.2.1"
    assert record.ttl == 300
