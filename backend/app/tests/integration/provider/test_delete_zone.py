from uuid import uuid4

from app.providers.base import DNSProvider


def test_delete_zone(provider: DNSProvider):
    zone_name = f"{uuid4().hex}.test.dev."

    provider.create_zone(zone_name)
    provider.delete_zone(zone_name)

    assert provider.get_zone(zone_name) is None
