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

Install the required dependency listed in [requirements.txt](requirements.txt). For a step-by-step setup guide, including how to use a virtual environment, see [INSTALL.md](INSTALL.md):

```bash
pip install -r requirements.txt
```


## Tests

Install the test dependencies and run the suite with:

```bash
pip install -r requirements.txt pytest requests-mock
pytest
```
