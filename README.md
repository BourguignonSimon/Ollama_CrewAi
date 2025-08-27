# Ollama_CrewAi

Ollama_CrewAi illustre une architecture **Manager ↔ Agents** minimaliste. Le manager lit un objectif, le découpe en tâches et les distribue aux agents qui rendent leur résultat. Ce dépôt fournit un orchestrateur de démonstration ainsi qu'un exemple de récupération HTTP conservé en annexe.

## Démarrage rapide

1. **Installation**

   ```bash
   git clone <repository-url>
   cd Ollama_CrewAi
   pip install .
   ```

2. **Lancer le scénario fourni**

   ```bash
   ollama-crewai-agents -c config/agents.yaml
   ```

   Exemple de session :

   ```text
   $ ollama-crewai-agents -c config/agents.yaml
   manager  | objective loaded
   planner  | plan feature
   developer| implement feature
   tester   | test feature
   ```

3. **Aller plus loin**

   Consultez le [tutoriel](docs/tutorial.md) pour une présentation guidée et le [guide d'extension](docs/extension.md) pour créer vos propres agents.

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
- `AGENTS_CONFIG`: Path to the agent configuration file used by
  `ollama-crewai-agents` (defaults to `config/agents.yaml`).
- `AGENTS_DEBUG`: When set to `1`, `true`, or `yes`, enables debug logging
  for agent orchestration.

You can set them inline when invoking the CLI:

```bash
FETCH_URL=https://example.org FETCH_LIMIT=50 ollama-crewai
AGENTS_CONFIG=config/agents.yaml AGENTS_DEBUG=1 ollama-crewai-agents
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

#### Superviseur ↔ Manager ↔ Agents

```text
Superviseur <-> Manager <-> Agents
```

Launch the orchestration from the command line:

```bash
ollama-crewai-agents -c config/agents.yaml
```

Example session:

```text
$ ollama-crewai-agents -c config/agents.yaml
manager  | objective loaded
planner  | plan feature
developer| implement feature
tester   | test feature
```

### Agent configuration and workflow

Agents are declared in a YAML or JSON file.  The manager loads this
configuration, splits the global ``objective`` into tasks, and
distributes them round-robin to the registered agents, collecting their
results as they complete the work.

Example configuration:

```yaml
objective: "plan feature. implement feature. test feature."
agents:
  planner: {}
  developer: {}
  tester: {}
```

Run the manager with the configuration file and optional debugging:

```bash
ollama-crewai-agents -c config/agents.yaml --debug
# or rely on environment variables
AGENTS_CONFIG=config/agents.yaml AGENTS_DEBUG=1 ollama-crewai-agents
```

During execution the manager coordinates the agents and reports the
status of each task in the log output, providing a clear view of the
overall workflow.

## Annexe : `fetch_example`

Ce projet contient aussi un exemple minimaliste de récupération HTTP.
La fonction `fetch_example` télécharge les premiers caractères d'une URL
([example.com](https://example.com) par défaut) avec des paramètres pour
limiter la longueur du texte, le délai et le nombre de tentatives.

### Utilisation

```bash
python src/main.py
```

Les arguments de `fetch_example` dans `src/main.py` permettent de
personnaliser l'URL, la longueur du résultat ou encore le nombre de
reprises en cas d'échec.

## Possible extensions

- Accept command-line arguments for URL and character limit.
- Integrate asynchronous fetching or caching mechanisms.
- [Create custom agents](docs/extension.md).

## Contributing

Contributions are welcome:

1. Fork the repository and create a new branch.
2. Make your changes and ensure the tests pass.
3. Submit a pull request for review.
