from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

from contextlib import asynccontextmanager  # <--- NOUVEL IMPORT

from app.database import engine, Base

# --- Gestion du cycle de vie (Startup / Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Fonction de gestion du cycle de vie de l'application.
    
    Tout ce qui est AVANT le 'yield' est exécuté au DÉMARRAGE (Startup).
    Tout ce qui est APRÈS le 'yield' est exécuté à l'ARRÊT (Shutdown).
    """
    # Startup : Création des tables de la base de données
    print("Démarrage de l'application : Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("Base de données prête.")
    
    yield  # L'application est en cours d'exécution ici
    
    # Shutdown : Fermeture des connexions, logs de fin, etc.
    print("Arrêt de l'application.")

# Initialisation de l'application avec métadonnées pour OpenAPI
app = FastAPI(
    title="Health RAG API",
    description=(
        "API démonstrative utilisant l'architecture RAG (Retrieval-Augmented Generation). "
        "Cette application se connecte à l'API OpenFDA pour ingérer des données médicales, "
        "les vectorise via ChromaDB et permet de poser des questions en langage naturel."
    ),
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Support Technique",
        "email": "support@healthrag.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,  # <--- On relie ici notre fonction de cycle de vie
)

# Configuration du middleware CORS pour autoriser les appels cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion du routeur principal
app.include_router(router, prefix="/api/v1", tags=["RAG Operations"])

@app.get("/", tags=["Health Check"])
def read_root():
    """
    Endpoint de vérification de santé de l'API.
    
    Returns:
        dict: Un message de bienvenue.
    """
    return {"status": "online", "message": "API Health RAG sécurisée opérationnelle"}

if __name__ == "__main__":
    import uvicorn
    # Lancement du serveur de développement
    uvicorn.run(app, host="0.0.0.0", port=8000)