from app.config import ENV_CONFIG
from fastapi import Header, HTTPException, status


def authenticate_watcher(
    x_watcher_secret: str | None = Header(default=None),
    x_watcher_name: str | None = Header(default=None),
) -> str:
    if x_watcher_secret != ENV_CONFIG.WATCHER_AUTH_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid watcher authentication credentials",
        )

    if not x_watcher_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Watcher name is required",
        )

    return x_watcher_name
