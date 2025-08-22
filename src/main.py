import requests
import requests.exceptions


def fetch_example():
    """Fetch a snippet from example.com to demonstrate a dependency."""
    try:
        response = requests.get("https://example.com", timeout=10)
    except requests.exceptions.RequestException as exc:
        return f"Error fetching data: {exc}"
    if response.ok:
        return response.text[:100]
    return "Error fetching data"


if __name__ == "__main__":
    print(fetch_example())
