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

## Supervision humaine

Pendant l'exécution, un superviseur humain peut valider ou ajuster les
plans proposés par le manager. Les messages saisis par le superviseur sont
transmis au manager, qui les relaie ensuite aux agents pour guider la
progression du projet.

## Logging

The framework uses a structured logger configured via `core.logging`. Each
entry includes the log level, the emitting agent and the task identifier:

```
INFO|developer|1|completed
```

The logger is automatically injected into all agents and the manager, so
logs are emitted during task processing without extra setup.

## Resuming and stopping a workflow

The manager can persist its progress to a JSON file via the :class:`Storage`
utility. When a storage backend is supplied, the manager loads any previously
saved tasks, supervisor decisions and messages at startup. The state is
serialised after every update, allowing the process to be stopped at any time
and later resumed by constructing the manager with the same storage file.

```python
from core import Storage
storage = Storage("state.json")
manager = Manager(agents, bus=bus, storage=storage)
await manager.run("objective")
```

This flow makes it easy to interrupt a project and continue later without
losing context from the earlier conversation.

For instructions on creating vos propres agents personnalisés, consultez
[le guide d'extension](extension.md).
