from uuid import uuid4

import pytest
from app.providers.base import DNSProvider
from app.providers.factory import get_dns_provider


@pytest.fixture
def provider() -> DNSProvider:
    return get_dns_provider()


@pytest.fixture
def test_zone(provider: DNSProvider):
    zone_name = f"{uuid4().hex}.test.dev."

    provider.create_zone(zone_name)

    try:
        yield zone_name
    finally:
        provider.delete_zone(zone_name)
