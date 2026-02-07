"""
Custom exceptions for the application.
"""
from typing import Any, Optional


class HealthRAGException(Exception):
    """Base exception for all application errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(HealthRAGException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, status_code=401, details=details)


class AuthorizationError(HealthRAGException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Insufficient permissions", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, status_code=403, details=details)


class NotFoundError(HealthRAGException):
    """Raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, status_code=404, details=details)


class ValidationError(HealthRAGException):
    """Raised when validation fails."""
    
    def __init__(self, message: str = "Validation error", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, status_code=422, details=details)


class ConflictError(HealthRAGException):
    """Raised when there's a conflict (e.g., duplicate resource)."""
    
    def __init__(self, message: str = "Resource conflict", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, status_code=409, details=details)


class ExternalServiceError(HealthRAGException):
    """Raised when an external service fails."""
    
    def __init__(
        self,
        message: str = "External service error",
        service_name: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ):
        details = details or {}
        if service_name:
            details["service"] = service_name
        super().__init__(message=message, status_code=502, details=details)


class RateLimitError(HealthRAGException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, status_code=429, details=details)


class DatabaseError(HealthRAGException):
    """Raised when database operation fails."""
    
    def __init__(self, message: str = "Database error", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, status_code=500, details=details)
