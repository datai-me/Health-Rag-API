"""
Dependency injection for FastAPI endpoints.
"""
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError
from app.core.security import JWTHandler
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.fda_service import FDAService
from app.services.rag_service import RAGService

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """
    Get authentication service instance.
    
    Args:
        db: Database session
        
    Returns:
        AuthService instance
    """
    return AuthService(db)


def get_fda_service() -> FDAService:
    """
    Get FDA service instance.
    
    Returns:
        FDAService instance
    """
    return FDAService()


def get_rag_service() -> RAGService:
    """
    Get RAG service instance.
    
    Returns:
        RAGService instance
    """
    return RAGService()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT access token
        auth_service: Authentication service
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Decode token and extract username
        username = JWTHandler.get_token_subject(token)
        
        # Get user from database
        user = auth_service.get_current_user(username)
        
        return user
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


# Optional: Add role-based access control
def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (can be extended for user status checks).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current active user
    """
    # Future: Add checks for user.is_active, user.is_verified, etc.
    return current_user
