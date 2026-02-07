🩺 Health RAG API
Une application API moderne utilisant FastAPI, LangChain et OpenFDA pour démontrer une architecture RAG (Retrieval-Augmented Generation).

L'application permet d'ingérer des données médicales externes, de les vectoriser et de répondre à des questions complexes en langage naturel.

🏗️ Architecture
Backend : FastAPI (Python)
Orchestration IA : LangChain
Base de données vectorielle : ChromaDB
Modèle LLM : OpenAI GPT-3.5/4
Source de données : OpenFDA API
🚀 Installation
Cloner le repository
git clone https://github.com/votre-username/health_rag_api.gitcd health_rag_api
Créer un environnement virtuel
bash

python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
Installer les dépendances
bash

pip install -r requirements.txt
Configurer les variables d'environnement
Renommez le fichier .env et ajoutez votre clé API OpenAI :
env

OPENAI_API_KEY=sk-votre_cle_ici
▶️ Lancement du serveur
bash

python main.py
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
🛠️ Technologies utilisées
FastAPI
LangChain
ChromaDB
OpenAI API