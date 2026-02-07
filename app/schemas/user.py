"""
User schemas (DTOs) for request/response validation.
"""
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username (3-50 characters, alphanumeric and underscores only)",
        examples=["john_doe"]
    )


class UserCreate(UserBase):
    """Schema for user registration."""
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,  # Bcrypt limit
        description="Password (min 8 characters, must include uppercase, lowercase, digit, and special character)",
        examples=["SecureP@ss123"]
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Validate username format.
        
        Rules:
        - Only alphanumeric characters and underscores
        - Must start with a letter
        """
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError(
                "Username must start with a letter and contain only letters, numbers, and underscores"
            )
        return v
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password strength.
        
        Rules:
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", v):
            raise ValueError("Password must contain at least one special character")
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "john_doe",
                "password": "SecureP@ss123"
            }
        }
    }


class UserResponse(UserBase):
    """Schema for user data in responses."""
    
    id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "username": "john_doe",
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }
    }


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=72,
        description="New password (optional)"
    )
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: Optional[str]) -> Optional[str]:
        """Validate password strength if provided."""
        if v is None:
            return v
        
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", v):
            raise ValueError("Password must contain at least one special character")
        
        return v
