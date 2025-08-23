# Ollama_CrewAi

This project demonstrates how to fetch data from the web using Python's `requests` library. It provides a minimal example for educational purposes or as a base for experiments.

## Features

- Simple `fetch_example` function that retrieves a snippet from a specified URL (defaults to [example.com](https://example.com)) with configurable character limit, timeout, and retry behavior.
- Lightweight structure with a single dependency.

## Usage

Run the main script to display the first 100 characters returned by the site:

```bash
python src/main.py
```

You can customize the URL, length of the returned snippet, request timeout, and number of retries by passing arguments to `fetch_example` in `src/main.py`.

## Installation and Testing

Follow these steps to set up the project and run the test suite:

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Ollama_CrewAi
   ```

2. **(Optional) Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the package**

   To install the CLI and its dependencies:

   ```bash
   pip install .
   ```

   Alternatively, install the dependencies directly:

   ```bash
   pip install -r requirements.txt
   ```

4. **Install test dependencies and run the tests**

   ```bash
   pip install -r requirements.txt pytest requests-mock pytest-asyncio
   pytest
   ```

For a more detailed setup guide, including the use of virtual environments, see [INSTALL.md](INSTALL.md).

## Development

### Environment variables

The script honors several optional environment variables:

- `FETCH_URL`: URL to fetch (defaults to `https://example.com`).
- `FETCH_LIMIT`: Number of characters to display (defaults to `100`).
- `FETCH_TIMEOUT`: Timeout in seconds for the request (defaults to `10`).
- `FETCH_RETRIES`: Number of retry attempts for failed requests (defaults to `0`).

You can set them inline when invoking the CLI:

```bash
FETCH_URL=https://example.org FETCH_LIMIT=50 ollama-crewai
```

### Command-line usage

After installation the executable `ollama-crewai` is available. You can also run the module directly:

```bash
python src/main.py
```

### Agent orchestration CLI

The package also exposes a small orchestrator for the demo agents. Run
it with:

```bash
ollama-crewai-agents [-c config/agents.yaml] [--debug]
```

* `-c`, `--config` – path to the YAML or JSON configuration file
  describing the agents and default objective (defaults to
  `config/agents.yaml`).
* `--debug` – enable verbose logging to aid debugging.

The repository ships with a sample configuration file in `config/agents.yaml`.

## Possible extensions

- Accept command-line arguments for URL and character limit.
- Integrate asynchronous fetching or caching mechanisms.

## Contributing

Contributions are welcome:

1. Fork the repository and create a new branch.
2. Make your changes and ensure the tests pass.
3. Submit a pull request for review.
