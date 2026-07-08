from __future__ import annotations

import httpx
import pytest

from tests.integration.conftest import login, register_applicant

pytestmark = pytest.mark.integration


async def test_register_then_login_then_me(client: httpx.AsyncClient) -> None:
    tokens = await register_applicant(client, email="alice@example.com")
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    login_tokens = await login(client, email="alice@example.com", password="Str0ngPass!234")
    me = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {login_tokens['access_token']}"}
    )
    assert me.status_code == 200
    body = me.json()
    assert body["email"] == "alice@example.com"
    assert body["role"] == "applicant"


async def test_register_ignores_client_supplied_role(client: httpx.AsyncClient) -> None:
    """Self-registration must never be able to grant an elevated role — a
    security decision made in Phase 7. Regression-guard it at the API layer."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wannabe-officer@example.com",
            "password": "Str0ngPass!234",
            "full_name": "Wannabe Officer",
            "role": "officer",
        },
    )
    assert response.status_code == 201
    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )
    assert me.json()["role"] == "applicant"


async def test_duplicate_email_registration_conflicts(client: httpx.AsyncClient) -> None:
    await register_applicant(client, email="dupe@example.com")
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dupe@example.com",
            "password": "Str0ngPass!234",
            "full_name": "Dupe Again",
            "role": "applicant",
        },
    )
    assert response.status_code == 409


async def test_login_wrong_password_is_rejected(client: httpx.AsyncClient) -> None:
    await register_applicant(client, email="bob@example.com")
    response = await client.post(
        "/api/v1/auth/login", json={"email": "bob@example.com", "password": "WrongPass!234"}
    )
    assert response.status_code == 401


async def test_refresh_token_issues_a_new_working_access_token(client: httpx.AsyncClient) -> None:
    tokens = await register_applicant(client, email="carol@example.com")
    refreshed = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refreshed.status_code == 200
    new_tokens = refreshed.json()
    assert new_tokens["access_token"]
    # The old refresh token is single-use — rotated, not reusable.
    reuse = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert reuse.status_code == 401


async def test_me_requires_a_bearer_token(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
