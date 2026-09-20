class FlumeCliError(Exception):
    """Base class for all errors raised by this CLI."""


class ConfigError(FlumeCliError):
    """Raised when required configuration (env vars) is missing or invalid."""


class FlumeApiError(FlumeCliError):
    """Raised when the Flume API returns a non-2xx status or a success:false envelope."""

    def __init__(self, message, *, status_code=None, detailed=None):
        super().__init__(message)
        self.status_code = status_code
        self.detailed = detailed

    @classmethod
    def from_response(cls, response):
        try:
            body = response.json()
        except ValueError:
            return cls(
                f"Flume API request failed ({response.status_code}): {response.text}",
                status_code=response.status_code,
            )

        message = body.get("message") or body.get("http_message") or "Unknown error"
        detailed = body.get("detailed")
        text = f"Flume API request failed ({response.status_code}): {message}"
        if detailed:
            text += f" — {detailed}"
        return cls(text, status_code=response.status_code, detailed=detailed)


class AuthError(FlumeApiError):
    """Raised specifically for login/token-refresh failures."""


class RateLimitError(FlumeApiError):
    """Raised when the Flume API returns 429 (rate limit exceeded)."""

    @classmethod
    def from_response(cls, response):
        text = (
            "Flume API rate limit reached (429): you've hit Flume's ~120 requests/hour "
            "limit. Wait for it to reset (up to an hour) before retrying."
        )
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            text += f" Retry-After: {retry_after}."
        return cls(text, status_code=response.status_code)


class NetworkError(FlumeCliError):
    """Raised when a request fails before an HTTP response was received (timeout, DNS, etc)."""
