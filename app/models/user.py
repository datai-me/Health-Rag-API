"""
User database model.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db.base import Base


class User(Base):
    """
    User model for authentication.
    
    Attributes:
        id: Primary key
        username: Unique username
        hashed_password: Bcrypt hashed password
        created_at: Timestamp of user creation
        updated_at: Timestamp of last update
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
