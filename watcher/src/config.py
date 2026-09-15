from dataclasses import dataclass

from src.utils.env import get_env, get_env_literal


@dataclass(frozen=True)
class EnvConfig:
    REMOTE: bool = get_env_literal("REMOTE", {"TRUE", "FALSE"}) == "TRUE"
    # main instance variables
    API_HOST: str = get_env("API_HOST", "", True)
    HTTPS_ENABLED: bool = get_env_literal("HTTPS_ENABLED", {"TRUE", "FALSE"}, "FALSE") == "TRUE"
    # remote variables
    API_URL: str = get_env("API_URL", "", True)
    # watcher config
    WATCHER_NAME: str = get_env("WATCHER_NAME")
    WATCHER_AUTH_SECRET_KEY: str = get_env("WATCHER_AUTH_SECRET_KEY")
    TRAEFIK_HOST_IP: str = get_env("TRAEFIK_HOST_IP")
    # debug/advanced
    LOG_LEVEL: str = get_env_literal("LOG_LEVEL", {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}, "INFO")


ENV_CONFIG = EnvConfig

API_URL = (
    ENV_CONFIG.API_URL if ENV_CONFIG.REMOTE else f"{'https' if ENV_CONFIG.HTTPS_ENABLED else 'http'}://{ENV_CONFIG.API_HOST}/api"
)

__all__ = ["ENV_CONFIG"]
