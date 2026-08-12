import os
from typing import Optional, TypeVar

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
        raise ValueError(f"Environment variable {name} has an invalid value. Accepted options: {", ".join(options)}")
    
    return value


def get_env_int(name: str, default: str | None = None) -> int:
    value = get_env(name, default)

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Environment variable {name} must have an integer value.")