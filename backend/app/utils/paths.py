def join_url(*parts: str) -> str:
    return "/".join(part.strip("/") for part in parts)


def normalize_url(base_url: str) -> str:
    return base_url.lstrip("/")
