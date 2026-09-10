from uuid import uuid4

from app.models.record import DNSRecordProperties
from app.providers.base import DNSProvider


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


def test_get_nonexistent_record(provider: DNSProvider, test_zone: str):
    records = provider.get_record(
        zone_name=f"{test_zone}",
        name=f"{uuid4().hex}.test.dev.",
        type_="A",
    )

    assert records is None


def test_get_record_nonexistent_zone(provider: DNSProvider):
    records = provider.get_record(
        zone_name=f"{uuid4().hex}",
        name=f"{uuid4().hex}.test.dev.",
        type_="A",
    )

    assert records is None
