import requests


def fetch_example():
    """Fetch a snippet from example.com to demonstrate a dependency."""
    response = requests.get("https://example.com")
    if response.ok:
        return response.text[:100]
    return "Error fetching data"


if __name__ == "__main__":
    print(fetch_example())
