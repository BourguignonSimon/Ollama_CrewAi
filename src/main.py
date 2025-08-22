import logging
import os
from typing import Optional

import requests
import requests.exceptions


def fetch_example(url: Optional[str] = None, limit: Optional[int] = None) -> str:
    """Fetch a snippet from the specified URL.

    Args:
        url (str, optional): Web address to retrieve. Defaults to the
            ``FETCH_URL`` environment variable or ``"https://example.com"``.
        limit (int, optional): Maximum number of characters to return from the
            response body. Defaults to the ``FETCH_LIMIT`` environment variable
            or ``100``.

    Returns:
        str: A substring of the response body or an error message.

    Raises:
        ValueError: If ``limit`` is not a positive integer.
    """
    if url is None:
        url = os.getenv("FETCH_URL", "https://example.com")
    if limit is None:
        limit_str = os.getenv("FETCH_LIMIT")
        limit = int(limit_str) if limit_str is not None else 100
    if limit <= 0:
        raise ValueError("limit must be positive")

    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as exc:
        return f"Error fetching data: {exc}"
    if response.ok:
        return response.text[:limit]
    return "Error fetching data"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run example fetch and log the result."""
    logger.info(fetch_example())


if __name__ == "__main__":
    main()
