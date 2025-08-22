import pathlib
import sys

import pytest
import requests
import requests.exceptions

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
