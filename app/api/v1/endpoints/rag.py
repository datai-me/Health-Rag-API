"""
RAG (Retrieval-Augmented Generation) endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_fda_service, get_rag_service
from app.core.exceptions import ExternalServiceError, NotFoundError
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.rag import (
    AnswerResponse,
    AskRequest,
    IngestRequest,
    IngestResponse,
    SourceInfo,
)
from app.services.fda_service import FDAService
from app.services.rag_service import RAGService

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest drug data",
    description="Fetch drug information from OpenFDA and ingest into the RAG system"
)
async def ingest_drug(
    request: IngestRequest,
    current_user: User = Depends(get_current_user),
    fda_service: FDAService = Depends(get_fda_service),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Ingest drug data from OpenFDA API.
    
    This endpoint:
    1. Fetches drug information from OpenFDA
    2. Cleans and formats the data
    3. Ingests it into the RAG system for question answering
    
    - **drug_name**: Name of the drug to search (e.g., "aspirin", "ibuprofen")
    
    Returns information about the ingestion process.
    """
    logger.info(f"User {current_user.username} ingesting drug: {request.drug_name}")
    
    try:
        # Fetch raw data from FDA API
        raw_data = fda_service.fetch_drug_data(request.drug_name)
        
        # Clean and format the data
        formatted_texts = fda_service.clean_and_format_data(raw_data)
        
        # Ingest into RAG system
        chunks_created = rag_service.ingest_documents(formatted_texts)
        
        logger.info(
            f"Successfully ingested {request.drug_name}: {chunks_created} chunks created"
        )
        
        return IngestResponse(
            message="Drug data successfully ingested",
            drug_name=request.drug_name,
            chunks_created=chunks_created
        )
        
    except NotFoundError as e:
        logger.warning(f"Drug not found: {request.drug_name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    
    except ExternalServiceError as e:
        logger.error(f"External service error during ingestion: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=e.message
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during ingestion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest drug data"
        )


@router.post(
    "/ask",
    response_model=AnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question",
    description="Ask a question about ingested drugs using natural language"
)
async def ask_question(
    request: AskRequest,
    current_user: User = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Ask a question about ingested drug data.
    
    This endpoint uses RAG (Retrieval-Augmented Generation) to:
    1. Retrieve relevant information from the vector database
    2. Generate an answer using an LLM based on the retrieved context
    
    - **question**: Your question in natural language (e.g., "What are the side effects of aspirin?")
    
    Returns an AI-generated answer with source references.
    """
    logger.info(f"User {current_user.username} asking: {request.question[:100]}...")
    
    try:
        # Query the RAG system
        answer, raw_sources = rag_service.query(request.question)
        
        # Format sources
        sources = [
            SourceInfo(
                content_preview=source,
                source_type="OpenFDA",
                relevance_score=0.0  # Could be enhanced with actual relevance scores
            )
            for source in raw_sources
        ]
        
        logger.info(
            f"Successfully answered question for user {current_user.username} "
            f"with {len(sources)} sources"
        )
        
        return AnswerResponse(
            answer=answer,
            sources=sources,
            confidence=0.0  # Could be enhanced with actual confidence calculation
        )
        
    except ExternalServiceError as e:
        logger.error(f"RAG service error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=e.message
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during question answering: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process question"
        )


@router.delete(
    "/clear",
    status_code=status.HTTP_200_OK,
    summary="Clear knowledge base",
    description="Clear all ingested data from the RAG system (requires authentication)"
)
async def clear_knowledge_base(
    current_user: User = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Clear all ingested documents from the RAG system.
    
    This is useful for:
    - Testing
    - Resetting the knowledge base
    - Starting fresh with new data
    
    Warning: This operation cannot be undone.
    """
    logger.warning(f"User {current_user.username} clearing knowledge base")
    
    try:
        rag_service.clear_collection()
        
        logger.info(f"Knowledge base cleared by user {current_user.username}")
        
        return {
            "message": "Knowledge base cleared successfully",
            "cleared_by": current_user.username
        }
        
    except ExternalServiceError as e:
        logger.error(f"Failed to clear knowledge base: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    
    except Exception as e:
        logger.error(f"Unexpected error clearing knowledge base: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear knowledge base"
        )
