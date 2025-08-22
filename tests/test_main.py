import pathlib
import sys

import pytest
import requests
import requests.exceptions
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Ensure the src directory is on the path for imports
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from main import fetch_example


def test_fetch_example_success(requests_mock):
    requests_mock.get("https://example.com", text="Example Domain", status_code=200)
    assert fetch_example("https://example.com", limit=7) == "Example"


def test_fetch_example_http_error(requests_mock):
    requests_mock.get("https://example.com", status_code=404)
    assert fetch_example("https://example.com") == "Error fetching data"


def test_fetch_example_exception(requests_mock):
    requests_mock.get("https://example.com", exc=requests.exceptions.Timeout)
    result = fetch_example("https://example.com")
    assert result.startswith("Error fetching data:")


def test_fetch_example_invalid_limit():
    with pytest.raises(ValueError):
        fetch_example(limit=0)


def test_fetch_example_env_vars(requests_mock, monkeypatch):
    requests_mock.get("https://example.org", text="Example Domain", status_code=200)
    monkeypatch.setenv("FETCH_URL", "https://example.org")
    monkeypatch.setenv("FETCH_LIMIT", "7")
    assert fetch_example() == "Example"


def test_fetch_example_retries_adapter(requests_mock, monkeypatch):
    requests_mock.get("https://example.com", text="Example Domain", status_code=200)

    created: dict[str, Retry] = {}
    original_init = HTTPAdapter.__init__

    def fake_init(self, *args, **kwargs):  # type: ignore[override]
        created["max_retries"] = kwargs.get("max_retries")
        original_init(self, *args, **kwargs)

    monkeypatch.setattr(HTTPAdapter, "__init__", fake_init)

    assert fetch_example("https://example.com", limit=7, retries=3) == "Example"
    assert isinstance(created["max_retries"], Retry)
    assert created["max_retries"].total == 3


def test_fetch_example_env_timeout_and_retries(requests_mock, monkeypatch):
    requests_mock.get("https://example.com", text="Example Domain", status_code=200)
    monkeypatch.setenv("FETCH_TIMEOUT", "5")
    monkeypatch.setenv("FETCH_RETRIES", "1")

    captured: dict[str, int] = {}
    original_get = requests.Session.get

    def wrapped_get(self, url, **kwargs):  # type: ignore[override]
        captured["timeout"] = kwargs.get("timeout")
        return original_get(self, url, **kwargs)

    monkeypatch.setattr(requests.Session, "get", wrapped_get)

    assert fetch_example("https://example.com", limit=7) == "Example"
    assert captured["timeout"] == 5
