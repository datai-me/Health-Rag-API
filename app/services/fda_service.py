"""
FDA service for interacting with OpenFDA API.
"""
import requests
from typing import Dict, List

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError, NotFoundError
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class FDAService:
    """Service for interacting with OpenFDA API."""
    
    def __init__(self):
        """Initialize FDA service with configuration."""
        self.base_url = settings.fda_api_base_url
        self.timeout = settings.fda_request_timeout
        self.max_results = settings.fda_max_results
    
    def fetch_drug_data(self, drug_name: str) -> List[Dict]:
        """
        Fetch drug information from OpenFDA API.
        
        Args:
            drug_name: Name of the drug to search for
            
        Returns:
            List of drug information dictionaries
            
        Raises:
            NotFoundError: If drug is not found
            ExternalServiceError: If FDA API request fails
        """
        logger.info(f"Fetching drug data from FDA API for: {drug_name}")
        
        params = {
            "search": drug_name,
            "limit": self.max_results
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                logger.warning(f"No results found for drug: {drug_name}")
                raise NotFoundError(
                    message=f"No information found for drug: {drug_name}",
                    details={"drug_name": drug_name}
                )
            
            logger.info(f"Successfully fetched {len(results)} results for drug: {drug_name}")
            return results
            
        except requests.Timeout:
            logger.error(f"FDA API request timeout for drug: {drug_name}")
            raise ExternalServiceError(
                message="FDA API request timed out",
                service_name="OpenFDA",
                details={"drug_name": drug_name, "timeout": self.timeout}
            )
        
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Drug not found in FDA database: {drug_name}")
                raise NotFoundError(
                    message=f"Drug not found: {drug_name}",
                    details={"drug_name": drug_name}
                )
            else:
                logger.error(f"FDA API HTTP error for drug {drug_name}: {e}")
                raise ExternalServiceError(
                    message=f"FDA API error: {e.response.status_code}",
                    service_name="OpenFDA",
                    details={
                        "drug_name": drug_name,
                        "status_code": e.response.status_code,
                        "error": str(e)
                    }
                )
        
        except requests.RequestException as e:
            logger.error(f"FDA API request failed for drug {drug_name}: {e}")
            raise ExternalServiceError(
                message="Failed to connect to FDA API",
                service_name="OpenFDA",
                details={"drug_name": drug_name, "error": str(e)}
            )
    
    def clean_and_format_data(self, raw_data: List[Dict]) -> List[str]:
        """
        Clean and format raw FDA API data into readable text.
        
        Args:
            raw_data: Raw data from FDA API
            
        Returns:
            List of formatted text strings
        """
        logger.info(f"Cleaning and formatting {len(raw_data)} drug records")
        
        formatted_texts = []
        
        for item in raw_data:
            try:
                openfda = item.get("openfda", {})
                
                # Extract drug name
                brand_name = self._extract_first(openfda, "brand_name")
                generic_name = self._extract_first(openfda, "generic_name")
                drug_name = brand_name if brand_name != "Not specified" else generic_name
                
                # Extract key information
                usage = self._extract_first(item, "indications_and_usage")
                warnings = self._extract_first(item, "warnings")
                adverse_reactions = self._extract_first(item, "adverse_reactions")
                dosage = self._extract_first(item, "dosage_and_administration")
                
                # Format as readable text
                content = self._format_drug_text(
                    drug_name=drug_name,
                    usage=usage,
                    warnings=warnings,
                    adverse_reactions=adverse_reactions,
                    dosage=dosage
                )
                
                formatted_texts.append(content)
                
            except Exception as e:
                logger.warning(f"Error formatting drug record: {e}")
                continue
        
        logger.info(f"Successfully formatted {len(formatted_texts)} drug records")
        return formatted_texts
    
    def _extract_first(self, data: Dict, key: str) -> str:
        """
        Extract first value from a field in the data.
        
        Args:
            data: Dictionary containing the data
            key: Key to extract
            
        Returns:
            First value if exists, otherwise "Not specified"
        """
        value = data.get(key)
        
        if value and isinstance(value, list) and len(value) > 0:
            # Clean up the text: remove excessive whitespace
            text = value[0].strip()
            # Limit length for very long texts
            return text[:1000] if len(text) > 1000 else text
        
        return "Not specified"
    
    def _format_drug_text(
        self,
        drug_name: str,
        usage: str,
        warnings: str,
        adverse_reactions: str,
        dosage: str
    ) -> str:
        """
        Format drug information into a readable text.
        
        Args:
            drug_name: Name of the drug
            usage: Usage information
            warnings: Warning information
            adverse_reactions: Adverse reactions information
            dosage: Dosage information
            
        Returns:
            Formatted text string
        """
        sections = [
            f"Drug Name: {drug_name}",
            f"Indications and Usage: {usage}",
            f"Warnings: {warnings}",
            f"Adverse Reactions: {adverse_reactions}",
            f"Dosage and Administration: {dosage}"
        ]
        
        return "\n\n".join(sections)
