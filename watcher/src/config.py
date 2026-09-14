from dataclasses import dataclass

from src.utils.env import get_env, get_env_int, get_env_literal


@dataclass(frozen=True)
class EnvConfig:
    API_HOST: str = get_env("API_HOST", "dns-manager-backend", True)
    API_PORT: int = get_env_int("API_PORT", 9000)
    HTTPS_ENABLED: bool = get_env_literal("HTTPS_ENABLED", {"TRUE", "FALSE"}, "FALSE") == "TRUE"
    WATCHER_AUTHENTICATION_SECRET_KEY: str = get_env("WATCHER_AUTHENTICATION_SECRET_KEY", "", True)
    WATCHER_NAME: str = get_env("WATCHER_NAME")
    TRAEFIK_HOST_IP: str = get_env("TRAEFIK_HOST_IP")
    # debug/advanced
    LOG_LEVEL: str = get_env_literal("LOG_LEVEL", {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}, "INFO")


ENV_CONFIG = EnvConfig

__all__ = ["ENV_CONFIG"]
