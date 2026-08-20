import logging

from app.config import ENV_CONFIG
from app.providers.base import DNSProvider
from app.providers.powerdns.adapter import PowerDNSAdapter

logger = logging.getLogger(__name__)


def get_dns_provider() -> DNSProvider:
    match ENV_CONFIG.DNS_PROVIDER:
        case "powerdns":
            return PowerDNSAdapter()
        case _:
            logger.critical(
                "Invalid DNS provider configured: %r. The application cannot start and will now shut down.",
                ENV_CONFIG.DNS_PROVIDER,
            )
            raise SystemExit(1)


provider = get_dns_provider()

__all__ = ["provider"]
