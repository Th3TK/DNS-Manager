from dataclasses import dataclass

from app.utils.env import get_env, get_env_int, get_env_literal


@dataclass(frozen=True)
class EnvConfig:
    # dns provider selection
    DNS_PROVIDER: str = get_env_literal("DNS_PROVIDER", {"powerdns"})
    # powerdns options
    POWERDNS_API_URL: str = get_env("POWERDNS_API_URL", "", True)
    POWERDNS_API_KEY: str = get_env("POWERDNS_API_KEY", "", True)
    POWERDNS_SERVER_ID: str = get_env("POWERDNS_SERVER_ID", "", True)
    # database options
    DATABASE_URL: str = get_env("DATABASE_URL")
    # app options
    AUTHENTICATION_SECRET_KEY: str = get_env("AUTHENTICATION_SECRET_KEY")
    CHECK_INTERVAL_SECONDS: int = get_env_int("CHECK_INTERVAL_SECONDS", "300")
    ITEM_TRASH_INTERVAL_SECONDS: int = get_env_int("ITEM_TRASH_INTERVAL_SECONDS", "2592000")
    MANAGED_ZONE: str = get_env("MANAGED_ZONE", "", True)
    # debug/advanced
    LOG_LEVEL: str = get_env_literal("LOG_LEVEL", {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}, "INFO")
    AUTHENTICATION_ALGORITHM: str = get_env("AUTHENTICATION_ALGORITHM", "HS256")
    ACCESS_TOKEN_LIFETIME_SECONDS: int = get_env_int("ACCESS_TOKEN_LIFETIME_SECONDS", "3600")
    REFRESH_TOKEN_LIFETIME_SECONDS: int = get_env_int("REFRESH_TOKEN_LIFETIME_SECONDS", "259200")

ENV_CONFIG = EnvConfig()