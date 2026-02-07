"""
Authentication schemas (DTOs) for request/response validation.
"""
from typing import Optional

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Response schema for successful authentication."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class TokenPayload(BaseModel):
    """Internal schema for JWT token payload."""
    
    sub: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None


class LoginRequest(BaseModel):
    """Request schema for user login."""
    
    username: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Username",
        examples=["john_doe"]
    )
    password: str = Field(
        ...,
        min_length=1,
        description="Password",
        examples=["SecureP@ss123"]
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "john_doe",
                "password": "SecureP@ss123"
            }
        }
    }
