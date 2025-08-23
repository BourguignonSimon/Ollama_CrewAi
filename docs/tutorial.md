# Tutorial

This tutorial walks through configuring agents and running a workflow with the manager.

## Architecture

![Manager and agents](architecture.svg)

## Configuration

Agents are declared in a YAML or JSON file. Example `config/agents.yaml`:

```yaml
objective: "plan feature. implement feature. test feature."
agents:
  planner: {}
  developer: {}
  tester: {}
```

## Running the workflow

Execute the manager via the CLI:

```bash
ollama-crewai-agents -c config/agents.yaml --debug
```

Environment variables may also be used to provide defaults:

```bash
AGENTS_CONFIG=config/agents.yaml AGENTS_DEBUG=1 ollama-crewai-agents
```

## Workflow overview

1. The manager reads the `objective` from the configuration.
2. It splits the objective into discrete tasks.
3. Tasks are dispatched round-robin to the agents.
4. Agents process tasks and report results back to the manager.

## Logging

The framework uses a structured logger configured via `core.logging`. Each
entry includes the log level, the emitting agent and the task identifier:

```
INFO|developer|1|completed
```

The logger is automatically injected into all agents and the manager, so
logs are emitted during task processing without extra setup.

## Resuming a workflow

The manager can persist its progress to a JSON file via the :class:`Storage`
utility. Tasks, supervisor decisions and the messages exchanged with the
manager are written after every update. To resume a previous run, provide the
same storage file when constructing the manager and load the saved data:

```python
from core import Storage
storage = Storage("state.json")
tasks, agents, decisions, messages = storage.load()
```

This allows interrupted projects to continue without losing context from the
earlier conversation.
