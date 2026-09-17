import logging
from dataclasses import dataclass

from app.utils.env import get_env, get_env_int, get_env_literal, get_nameservers_env, get_watcher_managed_zone_env

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EnvConfig:
    # dns configuration
    DNS_PROVIDER: str
    DNS_RESOLVER: str
    NAMESERVERS: list[str]
    # powerdns
    POWERDNS_API_URL: str
    POWERDNS_API_KEY: str
    POWERDNS_SERVER_ID: str
    # database options
    DATABASE_URL: str
    # app options
    AUTH_SECRET_KEY: str
    WATCHER_AUTH_SECRET_KEY: str
    CHECK_INTERVAL_SECONDS: int
    MANAGED_ZONE: str | None
    HTTPS_ENABLED: bool
    # debug/advanced
    LOG_LEVEL: str
    AUTHENTICATION_ALGORITHM: str
    ACCESS_TOKEN_LIFETIME_SECONDS: int
    REFRESH_TOKEN_LIFETIME_SECONDS: int


def load_env_config() -> EnvConfig:
    try:
        return EnvConfig(
            DNS_PROVIDER=get_env_literal("DNS_PROVIDER", {"powerdns"}),
            DNS_RESOLVER=get_env("DNS_RESOLVER"),
            NAMESERVERS=get_nameservers_env("NAMESERVERS"),
            POWERDNS_API_URL=get_env("POWERDNS_API_URL", "", True),
            POWERDNS_API_KEY=get_env("POWERDNS_API_KEY", "", True),
            POWERDNS_SERVER_ID=get_env("POWERDNS_SERVER_ID", "", True),
            DATABASE_URL=get_env("DATABASE_URL"),
            AUTH_SECRET_KEY=get_env("AUTH_SECRET_KEY"),
            WATCHER_AUTH_SECRET_KEY=get_env("WATCHER_AUTH_SECRET_KEY"),
            CHECK_INTERVAL_SECONDS=get_env_int("CHECK_INTERVAL_SECONDS", 300),
            MANAGED_ZONE=get_watcher_managed_zone_env("MANAGED_ZONE"),
            HTTPS_ENABLED=get_env_literal("HTTPS_ENABLED", {"TRUE", "FALSE"}, "FALSE") == "TRUE",
            LOG_LEVEL=get_env_literal("LOG_LEVEL", {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}, "INFO"),
            ACCESS_TOKEN_LIFETIME_SECONDS=get_env_int("ACCESS_TOKEN_LIFETIME_SECONDS", 3600),
            REFRESH_TOKEN_LIFETIME_SECONDS=get_env_int("REFRESH_TOKEN_LIFETIME_SECONDS", 259200),
            AUTHENTICATION_ALGORITHM="HS256",
        )
    except ValueError as exc:
        logger.critical("Invalid environment configuration: %s Exiting.", exc)
        raise SystemExit(1)


ENV_CONFIG = load_env_config()

__all__ = ["ENV_CONFIG"]
