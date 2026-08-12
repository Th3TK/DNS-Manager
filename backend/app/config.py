from dataclasses import dataclass

from app.utils.env import get_env, get_env_int, get_env_literal

@dataclass(frozen=True)
class EnvConfig:
    DNS_PROVIDER: str = get_env_literal("DNS_PROVIDER", {"powerdns"})
    POWERDNS_API_URL: str = get_env("POWERDNS_API_URL", "", True)
    POWERDNS_API_KEY: str = get_env("POWERDNS_API_URL", "", True)
    DATABASE_URL: str = get_env("DATABASE_URL")
    CHECK_INTERVAL_SECONDS: int = get_env_int("CHECK_INTERVAL_SECONDS", "300")
    MANAGED_ZONE: str = get_env("MANAGED_ZONE", "", True)
    LOG_LEVEL: str = get_env_literal("LOG_LEVEL", {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}, "INFO")

ENV_CONFIG = EnvConfig()