# test if health check correctly returns None
from app.models.exceptions import DNSProviderException
from app.providers.base import DNSProvider


def test_health_check(provider: DNSProvider):
    try:
        response = provider.health_check()
        assert response is None
    except Exception as exc:
        assert isinstance(exc, DNSProviderException)
