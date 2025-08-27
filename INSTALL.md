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
3. Make the command-line scripts available by installing the package:
   ```bash
   pip install -e .
   # or
   pipx install .
   ```
   A quick test ensures everything is wired up:
   ```bash
   ollama-crewai-agents -h
   ```
4. Run the application:
   ```bash
   python src/main.py
   ```

## Installation sur Windows 11

1. Installez Git pour Windows depuis [git-scm.com](https://git-scm.com/download/win) et suivez l'assistant pour l'ajouter au `PATH`.
2. Installez Python 3.11 ou version supérieure depuis [python.org](https://www.python.org/downloads/windows/) en cochant l'option **Add python.exe to PATH**.
3. Ouvrez PowerShell puis créez et activez un environnement virtuel :
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate
   ```
4. Installez les dépendances du projet :
   ```powershell
   pip install -r requirements.txt
   pip install -e .
   ```
5. Vérifiez l'installation :
   ```powershell
   ollama-crewai-agents -h
   ```
6. *(Optionnel)* Si vous souhaitez exécuter les exemples nécessitant des modèles locaux, installez un serveur Ollama sur votre machine en suivant les instructions officielles, puis assurez-vous qu'il est en cours d'exécution.
