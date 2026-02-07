"""
Security utilities for authentication and authorization.
"""
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError

settings = get_settings()


class PasswordHasher:
    """Handle password hashing and verification using bcrypt."""
    
    # Bcrypt has a maximum password length of 72 bytes
    MAX_PASSWORD_LENGTH = 72
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password as string
        """
        # Truncate to 72 characters as bcrypt limit
        password_bytes = password[:PasswordHasher.MAX_PASSWORD_LENGTH].encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to check against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            password_bytes = plain_password[:PasswordHasher.MAX_PASSWORD_LENGTH].encode("utf-8")
            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False


class JWTHandler:
    """Handle JWT token creation and validation."""
    
    @staticmethod
    def create_access_token(
        subject: str,
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[dict] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            subject: The subject of the token (usually username or user_id)
            expires_delta: Optional custom expiration time
            additional_claims: Optional additional claims to include in the token
            
        Returns:
            Encoded JWT token
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        
        to_encode = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        
        # Add any additional claims
        if additional_claims:
            to_encode.update(additional_claims)
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token to decode
            
        Returns:
            Decoded token payload
            
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            return payload
        except JWTError as e:
            raise AuthenticationError(
                message="Could not validate credentials",
                details={"error": str(e)}
            )
    
    @staticmethod
    def get_token_subject(token: str) -> str:
        """
        Extract the subject from a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Token subject (username)
            
        Raises:
            AuthenticationError: If token is invalid or subject is missing
        """
        payload = JWTHandler.decode_token(token)
        subject: Optional[str] = payload.get("sub")
        
        if subject is None:
            raise AuthenticationError(
                message="Token is missing subject claim",
                details={"payload": payload}
            )
        
        return subject


# Convenience functions for backward compatibility
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return PasswordHasher.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return PasswordHasher.verify_password(plain_password, hashed_password)


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None
) -> str:
    """Create a JWT access token."""
    return JWTHandler.create_access_token(subject, expires_delta, additional_claims)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    return JWTHandler.decode_token(token)
