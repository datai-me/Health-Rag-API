🩺 Health RAG API (Poetry Version)
Une application API moderne utilisant FastAPI, LangChain et OpenFDA pour démontrer une architecture RAG (Retrieval-Augmented Generation).

Ce projet utilise Poetry pour la gestion des dépendances et des environnements virtuels.

🏗️ Architecture
Backend : FastAPI (Python)
Orchestration IA : LangChain
Base de données vectorielle : ChromaDB
Modèle LLM : OpenAI GPT-3.5/4
Source de données : OpenFDA API
Gestionnaire de paquets : Poetry

🛠️ Prérequis
Python 3.9 ou supérieur
Poetry installé sur votre machine
Une clé API OpenAI

🚀 Installation (avec Poetry)
Cloner le repository
git clone https://github.com/votre-username/health_rag_api.gitcd health_rag_api

Installer les dépendances
Cette commande va créer un environnement virtuel isolé et installer toutes les librairies nécessaires.
bash

poetry install
Activer l'environnement virtuel (Optionnel)
bash

poetry shell
(Si vous n'activez pas le shell, vous devrez préfixer vos commandes par poetry run comme indiqué ci-dessous).
Configurer les variables d'environnement
Assurez-vous que le fichier .env existe à la racine et contient votre clé API :
env

OPENAI_API_KEY=sk-votre_cle_ici
▶️ Lancement du serveur
Utilisez Poetry pour lancer l'application. Cela garantit que les bonnes versions de librairies sont utilisées.

bash

# Si vous n'avez pas fait 'poetry shell', utilisez :
poetry run uvicorn main:app --reload

# Si vous avez activé l'environnement avec 'poetry shell', simplement :
uvicorn main:app --reload
L'API sera accessible à l'adresse : http://127.0.0.1:8000

La documentation interactive (Swagger UI) est disponible ici : http://127.0.0.1:8000/docs

📚 Utilisation (Endpoints)
1. Ingestion de données
Ajoutez des informations sur un médicament à la base de connaissances.

URL : POST /api/v1/ingest
Body (JSON) :
json

{
  "drug_name": "aspirin"
}
2. Poser une question
Interrogez l'assistant sur les médicaments ingérés.

URL : POST /api/v1/ask
Body (JSON) :
json

{
  "question": "Quels sont les effets secondaires de l'aspirine ?"
}
