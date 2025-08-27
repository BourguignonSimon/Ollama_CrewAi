# Installation

These steps describe how to set up the project and install its dependencies.

1. It is recommended to use a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   The project relies solely on local components; no OpenAI or LiteLLM
   API key is needed.
3. Run the application:
   ```bash
   python src/main.py
   ```
