import ipaddress
import logging
from dataclasses import dataclass

from src.utils.env import get_env, get_env_ipv4, get_env_literal
from src.utils.url import is_valid_url

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EnvConfig:
    REMOTE: bool
    # main instance variables
    API_HOST: str
    HTTPS_ENABLED: bool
    # remote variables
    API_URL: str
    # watcher config
    WATCHER_NAME: str
    WATCHER_AUTH_SECRET_KEY: str
    TRAEFIK_HOST_IP: ipaddress.IPv4Address
    # debug/advanced
    LOG_LEVEL: str


def load_env_config() -> EnvConfig:
    try:
        return EnvConfig(
            REMOTE=get_env_literal("REMOTE", {"TRUE", "FALSE"}) == "TRUE",
            API_HOST=get_env("API_HOST", "", True),
            HTTPS_ENABLED=get_env_literal("HTTPS_ENABLED", {"TRUE", "FALSE"}, "FALSE") == "TRUE",
            API_URL=get_env("API_URL", "", True),
            WATCHER_NAME=get_env("WATCHER_NAME"),
            WATCHER_AUTH_SECRET_KEY=get_env("WATCHER_AUTH_SECRET_KEY"),
            TRAEFIK_HOST_IP=get_env_ipv4("TRAEFIK_HOST_IP"),
            LOG_LEVEL=get_env_literal("LOG_LEVEL", {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}, "INFO"),
        )
    except ValueError as exc:
        logger.critical("Invalid environment configuration: %s. Exiting.", exc)
        raise SystemExit(1)


def get_api_url(config: EnvConfig) -> str:
    if not config.REMOTE:
        return f"{'https' if ENV_CONFIG.HTTPS_ENABLED else 'http'}://{ENV_CONFIG.API_HOST}/api"

    if not is_valid_url(config.API_URL):
        logger.critical(
            "Invalid environment configuration: Invalid API_URL. Expected a valid URL, got %r. Exiting.", config.API_URL
        )
        raise SystemExit(1)

    return config.API_URL


ENV_CONFIG = load_env_config()
API_URL = get_api_url(ENV_CONFIG)

__all__ = ["ENV_CONFIG", "API_URL"]
