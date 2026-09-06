from fastapi import status


class DNSValidationError(ValueError):
    def __init__(self, detail: str, status_code: int = status.HTTP_422_UNPROCESSABLE_CONTENT):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class DNSProviderException(Exception):
    """Raised when the DNS provider cannot fulfill a request."""
