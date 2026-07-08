from __future__ import annotations

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.value_objects.enums import UserRole
from tests.integration.conftest import (
    auth_headers,
    login,
    mark_pending_review,
    register_applicant,
    seed_staff_user,
)
from tests.integration.test_applications_api import _create_application, _upload_all_artifacts

pytestmark = pytest.mark.integration


async def _submitted_application(client: httpx.AsyncClient) -> tuple[str, dict[str, str]]:
    tokens = await register_applicant(client, email="applicant-officer-flow@example.com")
    headers = auth_headers(tokens)
    app_id = await _create_application(client, headers)
    await _upload_all_artifacts(client, headers, app_id)
    submitted = await client.post(f"/api/v1/applications/{app_id}/submit", headers=headers)
    assert submitted.status_code == 200
    return app_id, headers


async def _officer_headers(client: httpx.AsyncClient, db_session: AsyncSession) -> dict[str, str]:
    await seed_staff_user(
        db_session,
        email="officer1@verifyco.bank",
        password="OfficerPass!234",
        full_name="Test Officer",
        role=UserRole.OFFICER,
        employee_code="EMP-TEST-1",
    )
    tokens = await login(client, email="officer1@verifyco.bank", password="OfficerPass!234")
    return auth_headers(tokens)


async def test_officer_can_view_evidence_and_record_a_decision(
    client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    app_id, _applicant_headers = await _submitted_application(client)
    await mark_pending_review(db_session, app_id)
    officer_headers = await _officer_headers(client, db_session)

    verification = await client.get(
        f"/api/v1/applications/{app_id}/verification", headers=officer_headers
    )
    assert verification.status_code == 200

    empty_reason = await client.post(
        f"/api/v1/applications/{app_id}/decision",
        headers=officer_headers,
        json={"decision": "approve", "reason": ""},
    )
    assert empty_reason.status_code == 422

    # Non-ASCII text (accented names, currency symbols, em-dashes) must round
    # -trip through Postgres correctly — a real regression this project hit
    # once already when a local dev cluster was initialized with SQL_ASCII
    # instead of UTF8 encoding (every ₹-denominated report would have failed).
    reason = "Évidence vérifiée — approuvé, montant ₹18,00,000."
    decided = await client.post(
        f"/api/v1/applications/{app_id}/decision",
        headers=officer_headers,
        json={"decision": "approve", "reason": reason},
    )
    assert decided.status_code == 200, decided.text
    assert decided.json()["decision"] == "approve"
    assert decided.json()["reason"] == reason

    detail = await client.get(f"/api/v1/applications/{app_id}", headers=officer_headers)
    assert detail.json()["status"] == "approved"
    assert detail.json()["decided_at"] is not None

    # Deciding an already-decided application is rejected.
    redecide = await client.post(
        f"/api/v1/applications/{app_id}/decision",
        headers=officer_headers,
        json={"decision": "reject", "reason": "Changed my mind."},
    )
    assert redecide.status_code == 409

    audit = await client.get(f"/api/v1/applications/{app_id}/audit", headers=officer_headers)
    assert audit.status_code == 200
    actions = {entry["action"] for entry in audit.json()}
    assert "officer_decision" in actions


async def test_applicant_role_is_denied_officer_endpoints(
    client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    app_id, applicant_headers = await _submitted_application(client)

    # 404, not 403 — `authorize_staff` uses the same existence-obscuring
    # pattern as ownership checks (see `authorize_view`/`authorize_owner`):
    # a non-staff caller isn't told whether the application even exists.
    verification = await client.get(
        f"/api/v1/applications/{app_id}/verification", headers=applicant_headers
    )
    assert verification.status_code == 404

    decision = await client.post(
        f"/api/v1/applications/{app_id}/decision",
        headers=applicant_headers,
        json={"decision": "approve", "reason": "n/a"},
    )
    assert decision.status_code == 403


async def test_auditor_can_read_but_not_decide(
    client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    app_id, _applicant_headers = await _submitted_application(client)
    await seed_staff_user(
        db_session,
        email="auditor1@verifyco.bank",
        password="AuditorPass!234",
        full_name="Test Auditor",
        role=UserRole.AUDITOR,
        employee_code="EMP-TEST-2",
    )
    tokens = await login(client, email="auditor1@verifyco.bank", password="AuditorPass!234")
    auditor_headers = auth_headers(tokens)

    verification = await client.get(
        f"/api/v1/applications/{app_id}/verification", headers=auditor_headers
    )
    assert verification.status_code == 200

    decision = await client.post(
        f"/api/v1/applications/{app_id}/decision",
        headers=auditor_headers,
        json={"decision": "approve", "reason": "n/a"},
    )
    assert decision.status_code == 403
