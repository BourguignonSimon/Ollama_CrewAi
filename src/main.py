import requests
import requests.exceptions


def fetch_example(url: str = "https://example.com", limit: int = 100) -> str:
    """Fetch a snippet from the specified URL.

    Args:
        url: Web address to retrieve.
        limit: Maximum number of characters to return from the response body.

    Returns:
        A substring of the response body or an error message.

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


if __name__ == "__main__":
    print(fetch_example(url="https://example.com", limit=100))
