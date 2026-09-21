import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from flume_cli.errors import ConfigError

BASE_URL = "https://api.flumewater.com"
TOKEN_CACHE_PATH = Path.home() / ".flume" / "token.json"

DEFAULT_UNITS = "GALLONS"
DEFAULT_BUCKET = "MIN"
DEFAULT_DEVICE_TYPE = 2  # water sensor (1 = bridge)
DEFAULT_OUTPUT = "flume_report.csv"

_ENV_VARS = ("FLUME_CLIENT_ID", "FLUME_CLIENT_SECRET", "FLUME_USERNAME", "FLUME_PASSWORD")

_dotenv_loaded = False


def load_dotenv_if_present():
    """Load a local .env file once, if present. No-op if there isn't one."""
    global _dotenv_loaded
    if not _dotenv_loaded:
        load_dotenv()
        _dotenv_loaded = True


@dataclass
class Credentials:
    client_id: str
    client_secret: str
    username: str
    password: str

    @classmethod
    def from_env(cls):
        values = {name: os.environ.get(name) for name in _ENV_VARS}
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise ConfigError(
                "Missing required environment variable(s): " + ", ".join(missing) +
                ". Set them in your shell, or in a .env file in the current directory "
                "(see .env.example)."
            )
        return cls(
            client_id=values["FLUME_CLIENT_ID"],
            client_secret=values["FLUME_CLIENT_SECRET"],
            username=values["FLUME_USERNAME"],
            password=values["FLUME_PASSWORD"],
        )
