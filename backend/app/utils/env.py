import os

from app.management.dns.validation import validate_dns_name
from app.models.exceptions import DNSValidationError


def get_env(name: str, default: str | None = None, accept_empty: bool = False) -> str:
    value = os.getenv(name, default)

    if value is None:
        raise ValueError(f"Environment variable {name} is not set!")
    if not accept_empty and value.strip() == "":
        raise ValueError(f"Environment variable {name} is empty!")

    return value


def get_env_literal(name: str, options: set[str], default: str | None = None) -> str:
    value = get_env(name, default)

    if value not in options:
        raise ValueError(f"Environment variable {name} has an invalid value. Accepted options: {', '.join(options)}")

    return value


def get_env_int(name: str, default: int | None = None) -> int:
    value = get_env(name, str(default))

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Environment variable {name} must have an integer value.")


def get_env_boolean(name: str, default: bool | None = None) -> bool:
    value = get_env(name, str(default))

    if value.lower() not in {"true", "false"}:
        raise ValueError(f"Environment variable {name} must have a boolean value.")

    return value.lower() == "true"


def get_nameservers_env(name: str) -> list[str]:
    value = get_env(name).replace(" ", "")

    values = value.split(",")

    for nameserver in values:
        try:
            validate_dns_name(nameserver)
        except DNSValidationError as exc:
            raise ValueError(f"Environment variable {name} contains invalid DNS names - {nameserver} - {str(exc)}")

    return list({f"{nameserver.rstrip('.')}." for nameserver in values})


def get_watcher_managed_zone_env(name: str) -> str | None:
    value = get_env(name, None, True)

    if not value or not value.rstrip("."):
        return None

    return f"{value.rstrip('.')}."
