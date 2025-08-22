# Ollama_CrewAi

This project demonstrates how to fetch data from the web using Python's `requests` library. It provides a minimal example for educational purposes or as a base for experiments.

## Features

- Simple `fetch_example` function that retrieves a snippet from a specified URL (defaults to [example.com](https://example.com)) with a configurable character limit.
- Lightweight structure with a single dependency.

## Usage

Run the main script to display the first 100 characters returned by the site:

```bash
python src/main.py
```

You can customize the URL and the length of the returned snippet by passing arguments to `fetch_example` in `src/main.py`.

## Installation

Install the project and its dependencies with:

```bash
pip install .
```

This will provide the CLI command `ollama-crewai`.

Alternatively, install the required dependency listed in [requirements.txt](requirements.txt):

```bash
pip install -r requirements.txt
```

For a step-by-step setup guide, including how to use a virtual environment, see [INSTALL.md](INSTALL.md).

## Development

### Tests

Install the test dependencies and run the suite with:

```bash
pip install -r requirements.txt pytest requests-mock
pytest
```

### Environment variables

The script honors two optional environment variables:

- `FETCH_URL`: URL to fetch (defaults to `https://example.com`).
- `FETCH_LIMIT`: Number of characters to display (defaults to `100`).

You can set them inline when invoking the CLI:

```bash
FETCH_URL=https://example.org FETCH_LIMIT=50 ollama-crewai
```

### Command-line usage

After installation the executable `ollama-crewai` is available. You can also run the module directly:

```bash
python src/main.py
```

## Possible extensions

- Accept command-line arguments for URL and character limit.
- Add retries or adjustable timeouts.
- Integrate asynchronous fetching or caching mechanisms.

## Contributing

Contributions are welcome:

1. Fork the repository and create a new branch.
2. Make your changes and ensure the tests pass.
3. Submit a pull request for review.
