import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .factories import UserFactory

@pytest.fixture
def api_client():
    return APIClient()

def test_unauthenticated_request_returns_403(api_client):
    # Note: When SessionAuthentication is enabled, DRF returns 403 Forbidden
    # instead of 401 Unauthorized for unauthenticated requests to avoid native browser auth prompts.
    url = reverse("api:fileversion-list")
    response = api_client.get(url)
    assert response.status_code == 403

def test_token_retrieval_with_valid_credentials_returns_200_and_token(api_client):
    password = "secretpassword123"
    user = UserFactory(password=password)
    
    url = "/auth-token/"
    data = {
        "username": user.email,
        "password": password
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 200
    assert "token" in response.data

def test_token_retrieval_with_invalid_credentials_returns_400(api_client):
    url = "/auth-token/"
    data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 400

def test_authenticated_request_returns_200(api_client):
    user = UserFactory()
    token = Token.objects.create(user=user)
    
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    url = reverse("api:fileversion-list")
    response = api_client.get(url)
    assert response.status_code == 200
