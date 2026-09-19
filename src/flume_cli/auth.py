import base64
import json
import time
from dataclasses import asdict, dataclass

from flume_cli.config import TOKEN_CACHE_PATH
from flume_cli.errors import AuthError

# Flume's docs only say "the JWT token needs to be decoded" to get the user_id,
# without naming the claim. Try these in order and use whichever is present.
_USER_ID_CLAIM_CANDIDATES = ("user_id", "userId", "id", "sub")

# Refresh a bit before actual expiry to avoid racing a request against expiry.
_EXPIRY_SAFETY_MARGIN_SECONDS = 60


@dataclass
class TokenSet:
    access_token: str
    refresh_token: str
    token_type: str
    expires_at: float
    user_id: int

    def is_expired(self):
        return time.time() >= (self.expires_at - _EXPIRY_SAFETY_MARGIN_SECONDS)


def decode_jwt_user_id(access_token):
    parts = access_token.split(".")
    if len(parts) != 3:
        raise AuthError("Access token does not look like a JWT (expected 3 dot-separated segments)")

    payload_segment = parts[1]
    padding = "=" * (-len(payload_segment) % 4)
    try:
        payload_bytes = base64.urlsafe_b64decode(payload_segment + padding)
        payload = json.loads(payload_bytes)
    except (ValueError, UnicodeDecodeError) as exc:
        raise AuthError(f"Could not decode JWT payload: {exc}") from exc

    for claim in _USER_ID_CLAIM_CANDIDATES:
        if claim in payload:
            try:
                return int(payload[claim])
            except (TypeError, ValueError):
                continue

    raise AuthError(
        "Could not find a user id claim in the access token. "
        f"Candidates tried: {_USER_ID_CLAIM_CANDIDATES}. "
        f"Claims present in token: {list(payload.keys())}"
    )


def _token_set_from_api_data(data):
    expires_at = time.time() + data["expires_in"]
    user_id = decode_jwt_user_id(data["access_token"])
    return TokenSet(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        token_type=data.get("token_type", "bearer"),
        expires_at=expires_at,
        user_id=user_id,
    )


def load_cached_token():
    try:
        raw = TOKEN_CACHE_PATH.read_text()
        return TokenSet(**json.loads(raw))
    except (FileNotFoundError, ValueError, TypeError, KeyError):
        return None


def save_token(token):
    TOKEN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE_PATH.write_text(json.dumps(asdict(token)))
    try:
        TOKEN_CACHE_PATH.chmod(0o600)
    except (NotImplementedError, OSError):
        pass  # best-effort; not all platforms (e.g. Windows) support POSIX file modes


def get_valid_token(client, creds):
    cached = load_cached_token()
    if cached and not cached.is_expired():
        return cached

    if cached:
        try:
            data = client.refresh(cached.refresh_token, creds)
            token = _token_set_from_api_data(data)
            save_token(token)
            return token
        except AuthError:
            pass  # fall through to a fresh login

    data = client.login(creds)
    token = _token_set_from_api_data(data)
    save_token(token)
    return token
