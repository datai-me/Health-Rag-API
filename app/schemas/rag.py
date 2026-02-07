"""
RAG schemas (DTOs) for request/response validation.
"""
from typing import List

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    """Request schema for ingesting drug data."""
    
    drug_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Drug name to search for in OpenFDA database",
        examples=["aspirin", "ibuprofen"]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "drug_name": "aspirin"
            }
        }
    }


class IngestResponse(BaseModel):
    """Response schema for successful ingestion."""
    
    message: str = Field(..., description="Success message")
    drug_name: str = Field(..., description="Name of the drug ingested")
    chunks_created: int = Field(..., description="Number of text chunks created and indexed", ge=0)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Drug data successfully ingested",
                "drug_name": "aspirin",
                "chunks_created": 15
            }
        }
    }


class AskRequest(BaseModel):
    """Request schema for asking questions."""
    
    question: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Question in natural language about ingested drugs",
        examples=["What are the side effects of aspirin?"]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "What are the side effects of aspirin?"
            }
        }
    }


class SourceInfo(BaseModel):
    """Schema for source information used in answer generation."""
    
    content_preview: str = Field(
        ...,
        description="Preview of the source content used for the answer",
        max_length=200
    )
    source_type: str = Field(
        default="OpenFDA",
        description="Type/origin of the source data"
    )
    relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance score of this source (0-1)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "content_preview": "Aspirin is used for pain relief and fever reduction. Common side effects include...",
                "source_type": "OpenFDA",
                "relevance_score": 0.95
            }
        }
    }


class AnswerResponse(BaseModel):
    """Response schema for question answering."""
    
    answer: str = Field(..., description="Generated answer from the LLM")
    sources: List[SourceInfo] = Field(
        default_factory=list,
        description="List of sources used to generate the answer"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the answer (0-1)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "Aspirin is commonly used for pain relief, fever reduction, and as an anti-inflammatory medication. Common side effects include stomach upset, heartburn, and in rare cases, bleeding.",
                "sources": [
                    {
                        "content_preview": "Aspirin is used for pain relief and fever reduction...",
                        "source_type": "OpenFDA",
                        "relevance_score": 0.95
                    }
                ],
                "confidence": 0.92
            }
        }
    }
