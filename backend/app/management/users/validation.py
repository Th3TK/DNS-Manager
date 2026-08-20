import re

from fastapi import HTTPException, status

USERNAME_PATTERN = re.compile(r"^[a-z0-9_@.+:$-]+$")
RESERVED_USERNAMES = {"system", "automatic"}


def validate_username(username: str) -> None:
    if not USERNAME_PATTERN.fullmatch(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username may only contain lowercase letters, digits, ':', '_' and '-'.",
        )

    if username in RESERVED_USERNAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{username}' is reserved.",
        )

    if username.startswith("watcher"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot start with 'watcher'.",
        )
