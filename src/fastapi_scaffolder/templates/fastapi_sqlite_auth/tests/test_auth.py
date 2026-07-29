import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_register_and_login_flow(client):
    # register
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "alice@example.com", "password": "supersecret123", "full_name": "Alice"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert "hashed_password" not in body  # never leak this

    # duplicate registration -> conflict
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "alice@example.com", "password": "supersecret123"},
    )
    assert resp.status_code == 409
    assert resp.json()["error_code"] == "conflict"

    # login with correct credentials (form-encoded, OAuth2 password flow)
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "alice@example.com", "password": "supersecret123"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

    # login with wrong password -> unauthorized
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "alice@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401
    assert resp.json()["error_code"] == "unauthorized"

    # access protected route with the token
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"


def test_me_without_token_is_unauthorized(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
    assert resp.json()["error_code"] == "unauthorized"


def test_me_with_garbage_token_is_unauthorized(client):
    resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


def test_register_validates_short_password(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "bob@example.com", "password": "short"},
    )
    assert resp.status_code == 422  # pydantic validation error, not our AppException


def test_register_validates_email_format(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "supersecret123"},
    )
    assert resp.status_code == 422


def test_google_login_redirects_to_google(client):
    resp = client.get("/api/v1/auth/google/login", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert "accounts.google.com" in resp.headers["location"]
