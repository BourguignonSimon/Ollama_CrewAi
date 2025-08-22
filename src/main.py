import argparse
import asyncio
import logging
import os
from typing import Optional

import aiohttp
import aiohttp.client_exceptions
import requests
import requests.exceptions
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def fetch_example(
    url: Optional[str] = None,
    limit: Optional[int] = None,
    timeout: Optional[int] = None,
    retries: Optional[int] = None,
) -> str:
    """Fetch a snippet from the specified URL.

    Args:
        url (str, optional): Web address to retrieve. Defaults to the
            ``FETCH_URL`` environment variable or ``"https://example.com"``.
        limit (int, optional): Maximum number of characters to return from the
            response body. Defaults to the ``FETCH_LIMIT`` environment variable
            or ``100``.
        timeout (int, optional): Number of seconds to wait for a response.
            Defaults to the ``FETCH_TIMEOUT`` environment variable or ``10``.
        retries (int, optional): Number of retry attempts for failed
            requests. Defaults to the ``FETCH_RETRIES`` environment variable or
            ``0``.

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
    if timeout is None:
        timeout_str = os.getenv("FETCH_TIMEOUT")
        timeout = int(timeout_str) if timeout_str is not None else 10
    if retries is None:
        retries_str = os.getenv("FETCH_RETRIES")
        retries = int(retries_str) if retries_str is not None else 0
    if limit <= 0:
        raise ValueError("limit must be positive")

    try:
        with requests.Session() as session:
            if retries > 0:
                retry_strategy = Retry(
                    total=retries,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["HEAD", "GET", "OPTIONS"],
                )
                adapter = HTTPAdapter(max_retries=retry_strategy)
            else:
                adapter = HTTPAdapter()
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            response = session.get(url, timeout=timeout)
    except requests.exceptions.RequestException as exc:
        return f"Error fetching data: {exc}"
    if response.ok:
        return response.text[:limit]
    return "Error fetching data"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_example_async(
    url: Optional[str] = None,
    limit: Optional[int] = None,
    timeout: Optional[int] = None,
    retries: Optional[int] = None,
) -> str:
    """Asynchronously fetch a snippet from the specified URL.

    Args:
        url (str, optional): Web address to retrieve. Defaults to the
            ``FETCH_URL`` environment variable or ``"https://example.com"``.
        limit (int, optional): Maximum number of characters to return from the
            response body. Defaults to the ``FETCH_LIMIT`` environment variable
            or ``100``.
        timeout (int, optional): Number of seconds to wait for a response.
            Defaults to the ``FETCH_TIMEOUT`` environment variable or ``10``.
        retries (int, optional): Number of retry attempts for failed
            requests. Defaults to the ``FETCH_RETRIES`` environment variable or
            ``0``.

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
    if timeout is None:
        timeout_str = os.getenv("FETCH_TIMEOUT")
        timeout = int(timeout_str) if timeout_str is not None else 10
    if retries is None:
        retries_str = os.getenv("FETCH_RETRIES")
        retries = int(retries_str) if retries_str is not None else 0
    if limit <= 0:
        raise ValueError("limit must be positive")

    for attempt in range(retries + 1):
        try:
            timeout_ctx = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=timeout_ctx) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        text = await response.text()
                        return text[:limit]
                    return "Error fetching data"
        except aiohttp.client_exceptions.ClientError as exc:
            if attempt == retries:
                return f"Error fetching data: {exc}"
    return "Error fetching data"


async def main_async() -> None:
    """Run example fetch asynchronously and log the result."""
    logger.info(await fetch_example_async())


def main() -> None:
    """Run example fetch and log the result."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--async", dest="use_async", action="store_true", help="Use asynchronous fetching"
    )
    args = parser.parse_args()
    if args.use_async:
        asyncio.run(main_async())
    else:
        logger.info(fetch_example())


if __name__ == "__main__":
    main()
