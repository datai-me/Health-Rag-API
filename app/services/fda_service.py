import requests
from typing import List, Dict

class FDAService:
    """Service responsable de l'interaction avec l'API OpenFDA."""
    BASE_URL = "https://api.fda.gov/drug/label.json"

    def fetch_drug_data(self, drug_name: str) -> List[Dict]:
        """Récupère les notices via l'API OpenFDA."""
        params = {"search": drug_name, "limit": 3}
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.RequestException as e:
            print(f"Erreur FDA API: {e}")
            return []

    def clean_and_format_data(self, raw_data: List[Dict]) -> List[str]:
        """Nettoie le JSON et crée du texte lisible pour le LLM."""
        texts = []
        for item in raw_data:
            openfda = item.get("openfda", {})
            name = openfda.get("brand_name", ["Inconnu"])[0]
            usage = self._extract_first(item, "indications_and_usage")
            warnings = self._extract_first(item, "warnings")
            reactions = self._extract_first(item, "adverse_reactions")
            
            content = f"Medicament: {name}. Usage: {usage}. Warnings: {warnings}. Side Effects: {reactions}"
            texts.append(content)
        return texts

    def _extract_first(self, data: Dict, key: str) -> str:
        val = data.get(key)
        return val[0] if val and isinstance(val, list) else "Non spécifié"