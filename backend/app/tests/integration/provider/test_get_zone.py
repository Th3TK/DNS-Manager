from uuid import uuid4

from app.models.zone import DNSZoneProperties
from app.providers.base import DNSProvider


def test_get_nonexistent_zone(provider: DNSProvider):
    zone_name = f"{uuid4().hex}.test.dev."

    assert provider.get_zone(zone_name) is None


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
