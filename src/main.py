import logging
import requests
import requests.exceptions


def fetch_example(url: str = "https://example.com", limit: int = 100) -> str:
    """Fetch a snippet from the specified URL.

    Args:
        url (str): Web address to retrieve.
        limit (int): Maximum number of characters to return from the response body.

    Returns:
        str: A substring of the response body or an error message.

    Raises:
        ValueError: If ``limit`` is not a positive integer.
    """
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
    logger.info(fetch_example(url="https://example.com", limit=100))


if __name__ == "__main__":
    main()
