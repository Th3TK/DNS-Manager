from uuid import uuid4

import pytest
from app.models.zone import DNSZoneProperties
from app.providers.base import DNSProvider
from fastapi import HTTPException


def test_create_zone(provider: DNSProvider):
    zone_name = f"{uuid4().hex}.test.dev."

    try:
        zone = provider.create_zone(zone_name)

        assert isinstance(zone, DNSZoneProperties)
        assert zone.name == zone_name
    finally:
        provider.delete_zone(zone_name)


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
