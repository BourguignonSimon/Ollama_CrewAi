# Création d'un agent personnalisé

Ce guide décrit comment ajouter un nouvel agent à **Ollama CrewAi**.

Pour une introduction complète au fonctionnement du manager et à la
configuration initiale, consultez le [tutoriel](tutorial.md).

## 1. Hériter de `Agent`

Créez une sous-classe de `agents.base.Agent` et implémentez les méthodes
obligatoires :

```python
from agents.base import Agent
from agents.message import Message

class MonAgent(Agent):
    def plan(self) -> Message:
        return Message(sender="mon_agent", content="prêt")

    def act(self, message: Message) -> Message:
        # traitement du message
        return Message(sender="mon_agent", content=message.content.upper(), metadata=message.metadata)

    def observe(self, message: Message) -> None:
        pass
```

## 2. Enregistrer l'agent auprès du manager

Instanciez un `Manager` puis enregistrez dynamiquement votre agent via
`register_agent` :

```python
from agents.manager import Manager

manager = Manager()
manager.register_agent("mon_agent", MonAgent())
```

Le manager se charge de connecter l'agent au bus de messages et de créer
sa file de messages.

Un exemple complet est disponible dans
[`examples/custom_agent.py`](../examples/custom_agent.py).
