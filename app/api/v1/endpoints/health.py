"""
Health check endpoint.
"""
from datetime import datetime

from fastapi import APIRouter, status

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Health RAG API"
    }


@router.get("/", status_code=status.HTTP_200_OK, tags=["Health"])
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        API information
    """
    return {
        "message": "Health RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }
