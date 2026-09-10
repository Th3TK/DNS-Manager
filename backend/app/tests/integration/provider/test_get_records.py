from uuid import uuid4

from app.providers.base import DNSProvider


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


def test_get_records_nonexistent_zone(provider: DNSProvider):
    zone_name = f"{uuid4().hex}.test.dev."

    assert provider.get_records(zone_name) is None
