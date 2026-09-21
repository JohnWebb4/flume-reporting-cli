from __future__ import annotations

import base64
import json
import time

import pytest

from flume_cli import auth
from flume_cli.config import Credentials
from flume_cli.errors import AuthError, RateLimitError


def _b64url(data: dict) -> str:
    raw = json.dumps(data).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _make_jwt(payload: dict, header: dict | None = None) -> str:
    header_segment = _b64url(header or {"alg": "none", "typ": "JWT"})
    payload_segment = _b64url(payload)
    return f"{header_segment}.{payload_segment}.signature"


def _make_token_set(**overrides):
    defaults = {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "token_type": "bearer",
        "expires_at": time.time() + 3600,
        "user_id": 42,
    }
    defaults.update(overrides)
    return auth.TokenSet(**defaults)


@pytest.fixture
def creds():
    return Credentials(
        client_id="client-id",
        client_secret="client-secret",
        username="user@example.com",
        password="hunter2",
    )


class TestDecodeJwtUserId:
    def test_returns_user_id_claim_when_present(self):
        token = _make_jwt({"user_id": 7})
        assert auth.decode_jwt_user_id(token) == 7

    @pytest.mark.parametrize("claim", ["user_id", "userId", "id", "sub"])
    def test_tries_each_candidate_claim(self, claim):
        token = _make_jwt({claim: 99})
        assert auth.decode_jwt_user_id(token) == 99

    def test_prefers_earlier_candidate_claim(self):
        token = _make_jwt({"user_id": 1, "sub": 2})
        assert auth.decode_jwt_user_id(token) == 1

    def test_skips_non_numeric_claim_and_falls_back(self):
        token = _make_jwt({"user_id": "not-a-number", "sub": "42"})
        assert auth.decode_jwt_user_id(token) == 42

    def test_raises_when_not_three_segments(self):
        with pytest.raises(AuthError, match="3 dot-separated segments"):
            auth.decode_jwt_user_id("only.two")

    def test_raises_on_invalid_base64_payload(self):
        with pytest.raises(AuthError, match="Could not decode JWT payload"):
            auth.decode_jwt_user_id("header.not-valid-base64!!!.signature")

    def test_raises_on_non_json_payload(self):
        payload_segment = base64.urlsafe_b64encode(b"not json").rstrip(b"=").decode()
        with pytest.raises(AuthError, match="Could not decode JWT payload"):
            auth.decode_jwt_user_id(f"header.{payload_segment}.signature")

    def test_raises_when_no_candidate_claim_present(self):
        token = _make_jwt({"unrelated": "value"})
        with pytest.raises(AuthError, match="Could not find a user id claim"):
            auth.decode_jwt_user_id(token)


class TestTokenSetIsExpired:
    def test_not_expired_when_well_before_expiry(self):
        token = _make_token_set(expires_at=time.time() + 3600)
        assert token.is_expired() is False

    def test_expired_once_past_expiry(self):
        token = _make_token_set(expires_at=time.time() - 1)
        assert token.is_expired() is True

    def test_expired_within_safety_margin_of_expiry(self):
        token = _make_token_set(expires_at=time.time() + 30)
        assert token.is_expired() is True


class TestLoadCachedToken:
    def test_returns_none_when_file_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(auth, "TOKEN_CACHE_PATH", tmp_path / "missing.json")
        assert auth.load_cached_token() is None

    def test_returns_token_set_from_valid_file(self, tmp_path, monkeypatch):
        path = tmp_path / "token.json"
        token = _make_token_set()
        path.write_text(json.dumps(auth.asdict(token)))
        monkeypatch.setattr(auth, "TOKEN_CACHE_PATH", path)

        loaded = auth.load_cached_token()

        assert loaded == token

    def test_returns_none_on_invalid_json(self, tmp_path, monkeypatch):
        path = tmp_path / "token.json"
        path.write_text("not json")
        monkeypatch.setattr(auth, "TOKEN_CACHE_PATH", path)
        assert auth.load_cached_token() is None

    def test_returns_none_on_missing_fields(self, tmp_path, monkeypatch):
        path = tmp_path / "token.json"
        path.write_text(json.dumps({"access_token": "only-this"}))
        monkeypatch.setattr(auth, "TOKEN_CACHE_PATH", path)
        assert auth.load_cached_token() is None


class TestSaveToken:
    def test_writes_readable_token_and_restricts_permissions(self, tmp_path, monkeypatch):
        path = tmp_path / "nested" / "token.json"
        monkeypatch.setattr(auth, "TOKEN_CACHE_PATH", path)
        token = _make_token_set()

        auth.save_token(token)

        assert auth.load_cached_token() == token
        assert (path.stat().st_mode & 0o777) == 0o600


class TestGetValidToken:
    def test_returns_cached_token_without_calling_client(self, tmp_path, monkeypatch, creds):
        path = tmp_path / "token.json"
        cached = _make_token_set(expires_at=time.time() + 3600)
        path.write_text(json.dumps(auth.asdict(cached)))
        monkeypatch.setattr(auth, "TOKEN_CACHE_PATH", path)

        client = FakeClient()
        result = auth.get_valid_token(client, creds)

        assert result == cached
        assert client.login_calls == []
        assert client.refresh_calls == []

    def test_refreshes_expired_cached_token(self, tmp_path, monkeypatch, creds):
        path = tmp_path / "token.json"
        cached = _make_token_set(expires_at=time.time() - 1, refresh_token="old-refresh")
        path.write_text(json.dumps(auth.asdict(cached)))
        monkeypatch.setattr(auth, "TOKEN_CACHE_PATH", path)

        new_access_token = _make_jwt({"user_id": 55})
        client = FakeClient(
            refresh_result={
                "access_token": new_access_token,
                "refresh_token": "new-refresh",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        )

        result = auth.get_valid_token(client, creds)

        assert client.refresh_calls == [("old-refresh", creds)]
        assert client.login_calls == []
        assert result.access_token == new_access_token
        assert result.refresh_token == "new-refresh"
        assert result.user_id == 55
        assert auth.load_cached_token() == result

    def test_propagates_rate_limit_error_without_falling_back_to_login(
        self, tmp_path, monkeypatch, creds
    ):
        path = tmp_path / "token.json"
        cached = _make_token_set(expires_at=time.time() - 1)
        path.write_text(json.dumps(auth.asdict(cached)))
        monkeypatch.setattr(auth, "TOKEN_CACHE_PATH", path)

        client = FakeClient(refresh_error=RateLimitError("rate limited"))

        with pytest.raises(RateLimitError):
            auth.get_valid_token(client, creds)

        assert client.login_calls == []

    def test_falls_back_to_login_when_refresh_raises_auth_error(
        self, tmp_path, monkeypatch, creds
    ):
        path = tmp_path / "token.json"
        cached = _make_token_set(expires_at=time.time() - 1)
        path.write_text(json.dumps(auth.asdict(cached)))
        monkeypatch.setattr(auth, "TOKEN_CACHE_PATH", path)

        new_access_token = _make_jwt({"user_id": 7})
        client = FakeClient(
            refresh_error=AuthError("refresh token expired"),
            login_result={
                "access_token": new_access_token,
                "refresh_token": "fresh-refresh",
                "token_type": "bearer",
                "expires_in": 3600,
            },
        )

        result = auth.get_valid_token(client, creds)

        assert len(client.refresh_calls) == 1
        assert client.login_calls == [creds]
        assert result.access_token == new_access_token
        assert result.user_id == 7
        assert auth.load_cached_token() == result

    def test_logs_in_fresh_when_no_cached_token(self, tmp_path, monkeypatch, creds):
        monkeypatch.setattr(auth, "TOKEN_CACHE_PATH", tmp_path / "missing.json")

        new_access_token = _make_jwt({"user_id": 3})
        client = FakeClient(
            login_result={
                "access_token": new_access_token,
                "refresh_token": "fresh-refresh",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        )

        result = auth.get_valid_token(client, creds)

        assert client.refresh_calls == []
        assert client.login_calls == [creds]
        assert result.user_id == 3
        assert auth.load_cached_token() == result


class FakeClient:
    """Minimal stand-in for FlumeClient's login/refresh methods."""

    def __init__(self, *, login_result=None, refresh_result=None, refresh_error=None):
        self._login_result = login_result
        self._refresh_result = refresh_result
        self._refresh_error = refresh_error
        self.login_calls = []
        self.refresh_calls = []

    def login(self, creds):
        self.login_calls.append(creds)
        return self._login_result

    def refresh(self, refresh_token, creds):
        self.refresh_calls.append((refresh_token, creds))
        if self._refresh_error is not None:
            raise self._refresh_error
        return self._refresh_result
