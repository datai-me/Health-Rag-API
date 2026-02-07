"""
Unit tests for authentication endpoints.
"""
import pytest
from fastapi import status


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_register_success(self, client, test_user_data):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == test_user_data["username"]
    
    def test_register_duplicate_username(self, client, test_user_data):
        """Test registration with duplicate username fails."""
        # First registration
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Second registration with same username
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_409_CONFLICT
    
    def test_register_weak_password(self, client):
        """Test registration with weak password fails."""
        weak_password_data = {
            "username": "testuser",
            "password": "weak"
        }
        
        response = client.post("/api/v1/auth/register", json=weak_password_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_success(self, client, test_user_data):
        """Test successful login."""
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, test_user_data):
        """Test login with invalid credentials fails."""
        # Register user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["username"],
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user(self, authenticated_client, test_user_data):
        """Test getting current user information."""
        response = authenticated_client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == test_user_data["username"]
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication fails."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestPasswordValidation:
    """Test password validation rules."""
    
    @pytest.mark.parametrize("password,should_fail", [
        ("short", True),  # Too short
        ("nouppercase1!", True),  # No uppercase
        ("NOLOWERCASE1!", True),  # No lowercase
        ("NoDigits!", True),  # No digits
        ("NoSpecial1", True),  # No special char
        ("ValidP@ss123", False),  # Valid password
    ])
    def test_password_strength(self, client, password, should_fail):
        """Test password strength validation."""
        user_data = {
            "username": "testuser",
            "password": password
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        if should_fail:
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        else:
            assert response.status_code == status.HTTP_201_CREATED
