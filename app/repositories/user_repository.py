"""
User repository for database operations.

This layer abstracts database operations from business logic,
following the Repository pattern.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import DatabaseError
from app.core.logging import get_logger
from app.models.user import User

logger = get_logger(__name__)


class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object if found, None otherwise
        """
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error fetching user by ID {user_id}: {e}")
            raise DatabaseError(f"Failed to fetch user by ID: {user_id}")
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User object if found, None otherwise
        """
        try:
            return self.db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"Error fetching user by username {username}: {e}")
            raise DatabaseError(f"Failed to fetch user by username: {username}")
    
    def create(self, username: str, hashed_password: str) -> User:
        """
        Create a new user.
        
        Args:
            username: Username for the new user
            hashed_password: Hashed password
            
        Returns:
            Created user object
            
        Raises:
            DatabaseError: If user creation fails
        """
        try:
            user = User(username=username, hashed_password=hashed_password)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Created new user: {username} (ID: {user.id})")
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user {username}: {e}")
            raise DatabaseError(f"Failed to create user: {username}")
    
    def update_password(self, user_id: int, new_hashed_password: str) -> Optional[User]:
        """
        Update user password.
        
        Args:
            user_id: ID of the user to update
            new_hashed_password: New hashed password
            
        Returns:
            Updated user object if found, None otherwise
            
        Raises:
            DatabaseError: If password update fails
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return None
            
            user.hashed_password = new_hashed_password
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Updated password for user ID: {user_id}")
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating password for user ID {user_id}: {e}")
            raise DatabaseError(f"Failed to update password for user ID: {user_id}")
    
    def delete(self, user_id: int) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            True if deleted, False if user not found
            
        Raises:
            DatabaseError: If deletion fails
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            self.db.delete(user)
            self.db.commit()
            logger.info(f"Deleted user ID: {user_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user ID {user_id}: {e}")
            raise DatabaseError(f"Failed to delete user ID: {user_id}")
    
    def exists_by_username(self, username: str) -> bool:
        """
        Check if user exists by username.
        
        Args:
            username: Username to check
            
        Returns:
            True if user exists, False otherwise
        """
        try:
            return self.db.query(User).filter(User.username == username).count() > 0
        except Exception as e:
            logger.error(f"Error checking user existence for {username}: {e}")
            raise DatabaseError(f"Failed to check user existence: {username}")
