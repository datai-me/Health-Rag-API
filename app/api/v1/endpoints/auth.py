"""
Authentication endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service, get_current_user
from app.core.exceptions import AuthenticationError, ConflictError
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account and receive an access token"
)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user.
    
    - **username**: 3-50 characters, alphanumeric and underscores only
    - **password**: Min 8 characters, must include uppercase, lowercase, digit, and special character
    
    Returns user information and access token.
    """
    try:
        user_response, token_response = auth_service.register(user_data)
        
        return {
            "message": "User registered successfully",
            "user": user_response,
            "access_token": token_response.access_token,
            "token_type": token_response.token_type
        }
        
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login",
    description="Authenticate and receive an access token"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login with username and password.
    
    - **username**: Your username
    - **password**: Your password
    
    Returns an access token for authenticated requests.
    """
    try:
        token_response = auth_service.login(
            username=form_data.username,
            password=form_data.password
        )
        return token_response
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout",
    description="Logout the current user (informational only, token invalidation handled client-side)"
)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout the current user.
    
    Note: JWT tokens are stateless. The client should discard the token.
    """
    return {
        "message": "Successfully logged out",
        "username": current_user.username
    }


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get information about the currently authenticated user"
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.
    
    Returns information about the authenticated user.
    """
    return UserResponse.model_validate(current_user)
