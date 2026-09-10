import pytest
from app.models.record import DNSRecordProperties
from app.providers.base import DNSProvider
from fastapi import HTTPException


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
