from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration de la base de données SQLite
# Le fichier sera créé automatiquement à la racine : database.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

# Création du moteur de base de données
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Création d'une session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour les modèles ORM
Base = declarative_base()

# Dépendance pour obtenir une session de base de données dans les routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()