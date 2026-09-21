import requests

from flume_cli.config import BASE_URL
from flume_cli.errors import AuthError, FlumeApiError, NetworkError, RateLimitError

REQUEST_TIMEOUT = 30


class FlumeClient:
    def __init__(self, base_url=BASE_URL, session=None):
        self.base_url = base_url
        self.session = session or requests.Session()
        self.session.headers["Content-Type"] = "application/json"

    def set_token(self, access_token):
        self.session.headers["Authorization"] = f"Bearer {access_token}"

    def _request(self, method, path, *, error_cls=FlumeApiError, **kwargs):
        try:
            response = self.session.request(
                method, f"{self.base_url}{path}", timeout=REQUEST_TIMEOUT, **kwargs
            )
        except requests.exceptions.Timeout:
            raise NetworkError(
                f"Timed out waiting for the Flume API after {REQUEST_TIMEOUT}s. "
                "Check your internet connection and try again."
            )
        except requests.exceptions.RequestException as exc:
            raise NetworkError(
                f"Could not reach the Flume API — check your internet connection. "
                f"(Details: {exc})"
            )

        try:
            body = response.json()
        except ValueError:
            body = None

        if not response.ok or body is None or not body.get("success", False):
            if response.status_code == 429:
                raise RateLimitError.from_response(response)
            raise error_cls.from_response(response)

        return body

    def login(self, creds):
        body = self._request(
            "POST",
            "/oauth/token",
            error_cls=AuthError,
            json={
                "grant_type": "password",
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "username": creds.username,
                "password": creds.password,
            },
        )
        return body["data"][0]

    def refresh(self, refresh_token, creds):
        body = self._request(
            "POST",
            "/oauth/token",
            error_cls=AuthError,
            json={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
            },
        )
        return body["data"][0]

    def fetch_user(self, user_id):
        body = self._request("GET", f"/users/{user_id}")
        return body["data"][0]

    def fetch_devices(self, user_id, *, type_=None, limit=50):
        devices = []
        offset = 0
        while True:
            params = {
                "limit": limit,
                "offset": offset,
                "sort_field": "id",
                "sort_direction": "ASC",
            }
            if type_ is not None:
                params["type"] = type_

            body = self._request("GET", f"/users/{user_id}/devices", params=params)
            page = body.get("data", [])
            devices.extend(page)

            if len(page) < limit:
                break
            offset += limit

        return devices

    def query_device(self, user_id, device_id, *, since, until, bucket="HR",
                      units="GALLONS", request_id="usage"):
        body = self._request(
            "POST",
            f"/users/{user_id}/devices/{device_id}/query",
            json={
                "queries": [
                    {
                        "request_id": request_id,
                        "bucket": bucket,
                        "since_datetime": since,
                        "until_datetime": until,
                        "units": units,
                    }
                ]
            },
        )
        data = body.get("data") or [{}]
        result = data[0]
        if request_id not in result:
            raise FlumeApiError(
                f"Query response for device {device_id} did not contain "
                f"expected request_id '{request_id}': got keys {list(result.keys())}"
            )
        return result[request_id]
