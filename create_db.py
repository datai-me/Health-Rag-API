from app.database import engine, Base
from app.models import User
from app.config import get_settings

def init_db():
    """
    Fonction pour créer toutes les tables définies dans Base.
    Base contient la liste de tous les modèles qui héritent de lui (ici : User)
    """
    print("Création de la base de données...")
    try:
        # Cette commande lit tous les modèles importés (User) et crée les tables dans SQLite
        Base.metadata.create_all(bind=engine)
        print("✅ Base de données et tables créées avec succès !")
    except Exception as e:
        print(f"❌ Erreur lors de la création : {e}")

if __name__ == "__main__":
    init_db()