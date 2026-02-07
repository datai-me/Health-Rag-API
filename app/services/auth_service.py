"""
Authentication service for business logic.
"""
from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, ConflictError
from app.core.logging import get_logger
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserResponse

settings = get_settings()
logger = get_logger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.user_repo = UserRepository(db)
    
    def register(self, user_data: UserCreate) -> tuple[UserResponse, TokenResponse]:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Tuple of (UserResponse, TokenResponse)
            
        Raises:
            ConflictError: If username already exists
        """
        logger.info(f"Attempting to register user: {user_data.username}")
        
        # Check if user already exists
        if self.user_repo.exists_by_username(user_data.username):
            logger.warning(f"Registration failed: username already exists: {user_data.username}")
            raise ConflictError(
                message="Username already taken",
                details={"username": user_data.username}
            )
        
        # Hash password and create user
        hashed_password = hash_password(user_data.password)
        user = self.user_repo.create(
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        # Generate access token
        access_token = create_access_token(
            subject=user.username,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        logger.info(f"User registered successfully: {user.username} (ID: {user.id})")
        
        return (
            UserResponse.model_validate(user),
            TokenResponse(access_token=access_token, token_type="bearer")
        )
    
    def login(self, username: str, password: str) -> TokenResponse:
        """
        Authenticate user and generate access token.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            TokenResponse with access token
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        logger.info(f"Login attempt for user: {username}")
        
        # Get user from database
        user = self.user_repo.get_by_username(username)
        
        # Verify user exists and password is correct
        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Login failed for user: {username}")
            raise AuthenticationError(
                message="Incorrect username or password",
                details={"username": username}
            )
        
        # Generate access token
        access_token = create_access_token(
            subject=user.username,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        logger.info(f"User logged in successfully: {username}")
        
        return TokenResponse(access_token=access_token, token_type="bearer")
    
    def get_current_user(self, username: str) -> User:
        """
        Get current user by username from token.
        
        Args:
            username: Username from JWT token
            
        Returns:
            User object
            
        Raises:
            AuthenticationError: If user not found
        """
        user = self.user_repo.get_by_username(username)
        
        if not user:
            logger.warning(f"User not found for token subject: {username}")
            raise AuthenticationError(
                message="User not found",
                details={"username": username}
            )
        
        return user
    
    def update_password(self, user_id: int, new_password: str) -> UserResponse:
        """
        Update user password.
        
        Args:
            user_id: User ID
            new_password: New plain text password
            
        Returns:
            Updated user response
            
        Raises:
            AuthenticationError: If user not found
        """
        logger.info(f"Updating password for user ID: {user_id}")
        
        hashed_password = hash_password(new_password)
        user = self.user_repo.update_password(user_id, hashed_password)
        
        if not user:
            raise AuthenticationError(
                message="User not found",
                details={"user_id": user_id}
            )
        
        logger.info(f"Password updated successfully for user ID: {user_id}")
        
        return UserResponse.model_validate(user)
