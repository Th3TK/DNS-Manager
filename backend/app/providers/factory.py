import logging

from app.config import ENV_CONFIG
from app.providers.base import DNSProvider
from app.providers.powerdns.adapter import PowerDNSAdapter_4_9_17

logger = logging.getLogger(__name__)


def get_dns_provider() -> DNSProvider:
    match ENV_CONFIG.DNS_PROVIDER:
        case "powerdns":
            return PowerDNSAdapter_4_9_17()
        case _:
            logger.critical(
                "Invalid DNS provider configured: %r.",
                ENV_CONFIG.DNS_PROVIDER,
            )
            logger.critical("Critical error occured during startup - EXITING")
            raise SystemExit(1)


provider = get_dns_provider()

__all__ = ["provider"]
