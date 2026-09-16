from urllib.parse import urlsplit


def join_url(*parts: str) -> str:
    return "/".join(part.strip("/") for part in parts).rstrip("/")


def normalize_url(base_url: str) -> str:
    return base_url.lstrip("/")


def is_valid_url(url: str) -> bool:
    if not url:
        return False

    parsed = urlsplit(url)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False

    return True
