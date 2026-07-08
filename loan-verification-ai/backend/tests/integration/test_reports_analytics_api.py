from __future__ import annotations

import uuid
from decimal import Decimal

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.value_objects.enums import Recommendation, RiskBand, UserRole
from app.infrastructure.db.models.risk_score import RiskScore
from tests.integration.conftest import (
    auth_headers,
    login,
    mark_pending_review,
    register_applicant,
    seed_staff_user,
)
from tests.integration.test_applications_api import _create_application, _upload_all_artifacts

pytestmark = pytest.mark.integration


async def _submitted_application(client: httpx.AsyncClient, email: str) -> str:
    tokens = await register_applicant(client, email=email)
    headers = auth_headers(tokens)
    app_id = await _create_application(client, headers)
    await _upload_all_artifacts(client, headers, app_id)
    submitted = await client.post(f"/api/v1/applications/{app_id}/submit", headers=headers)
    assert submitted.status_code == 200
    return app_id


async def _insert_risk_score(db_session: AsyncSession, application_id: str, band: RiskBand) -> None:
    db_session.add(
        RiskScore(
            id=uuid.uuid4(),
            application_id=uuid.UUID(application_id),
            score=Decimal("0.2") if band is RiskBand.LOW else Decimal("0.7"),
            band=band,
            recommendation=Recommendation.AUTO_APPROVE_CANDIDATE
            if band is RiskBand.LOW
            else Recommendation.HIGH_RISK_REJECT_CANDIDATE,
            confidence=Decimal("0.9"),
            component_scores={"face_match": 0.9},
            weights_snapshot={"face_match": 0.4},
            reasons=["seeded for integration test"],
            is_current=True,
        )
    )
    await db_session.commit()


async def _officer_headers(client: httpx.AsyncClient, db_session: AsyncSession) -> dict[str, str]:
    await seed_staff_user(
        db_session,
        email="reports-officer@verifyco.bank",
        password="OfficerPass!234",
        full_name="Reports Officer",
        role=UserRole.OFFICER,
        employee_code="EMP-TEST-REPORTS",
    )
    tokens = await login(client, email="reports-officer@verifyco.bank", password="OfficerPass!234")
    return auth_headers(tokens)


async def test_generate_and_download_application_report_all_formats(
    client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    app_id = await _submitted_application(client, "report-applicant@example.com")
    await _insert_risk_score(db_session, app_id, RiskBand.LOW)
    await mark_pending_review(db_session, app_id)
    officer_headers = await _officer_headers(client, db_session)

    decided = await client.post(
        f"/api/v1/applications/{app_id}/decision",
        headers=officer_headers,
        json={"decision": "approve", "reason": "Low risk, evidence checks out."},
    )
    assert decided.status_code == 200, decided.text

    for fmt, magic in [("pdf", b"%PDF-"), ("json", b"{"), ("csv", b"reference_no")]:
        generated = await client.post(
            f"/api/v1/applications/{app_id}/reports",
            headers=officer_headers,
            json={"format": fmt},
        )
        assert generated.status_code == 200, generated.text
        body = generated.json()
        assert body["application_id"] == app_id
        assert body["download_url"]

        downloaded = await httpx.AsyncClient().get(body["download_url"])
        assert downloaded.status_code == 200
        assert downloaded.content.startswith(magic)

        reissued = await client.get(
            f"/api/v1/reports/{body['id']}/download", headers=officer_headers
        )
        assert reissued.status_code == 200
        assert reissued.json()["download_url"]


async def test_bulk_export_rejects_pdf_and_covers_every_application(
    client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    app_low = await _submitted_application(client, "bulk-applicant-low@example.com")
    app_high = await _submitted_application(client, "bulk-applicant-high@example.com")
    await _insert_risk_score(db_session, app_low, RiskBand.LOW)
    await _insert_risk_score(db_session, app_high, RiskBand.HIGH)
    officer_headers = await _officer_headers(client, db_session)

    pdf_rejected = await client.post(
        "/api/v1/reports/bulk", headers=officer_headers, json={"format": "pdf"}
    )
    assert pdf_rejected.status_code == 422

    csv_export = await client.post(
        "/api/v1/reports/bulk", headers=officer_headers, json={"format": "csv"}
    )
    assert csv_export.status_code == 200
    assert csv_export.json()["application_id"] is None

    downloaded = await httpx.AsyncClient().get(csv_export.json()["download_url"])
    assert downloaded.status_code == 200
    text = downloaded.content.decode("utf-8")
    # Header + one row per application (order not guaranteed).
    assert text.count("\n") >= 2
    assert "low" in text
    assert "high" in text


async def test_analytics_summary_reflects_seeded_data(
    client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    app_a = await _submitted_application(client, "analytics-a@example.com")
    app_b = await _submitted_application(client, "analytics-b@example.com")
    await _insert_risk_score(db_session, app_a, RiskBand.LOW)
    await _insert_risk_score(db_session, app_b, RiskBand.HIGH)
    await mark_pending_review(db_session, app_a)
    await mark_pending_review(db_session, app_b)
    officer_headers = await _officer_headers(client, db_session)

    decided_a = await client.post(
        f"/api/v1/applications/{app_a}/decision",
        headers=officer_headers,
        json={"decision": "approve", "reason": "ok"},
    )
    assert decided_a.status_code == 200, decided_a.text
    decided_b = await client.post(
        f"/api/v1/applications/{app_b}/decision",
        headers=officer_headers,
        json={"decision": "reject", "reason": "high risk"},
    )
    assert decided_b.status_code == 200, decided_b.text

    summary = await client.get("/api/v1/analytics", headers=officer_headers)
    assert summary.status_code == 200
    body = summary.json()
    assert body["total_applications"] == 2
    assert body["approved_count"] == 1
    assert body["rejected_count"] == 1
    assert body["approval_rate"] == 0.5
    assert body["risk_band_counts"]["low"] == 1
    assert body["risk_band_counts"]["high"] == 1


async def test_reports_and_analytics_are_staff_only(client: httpx.AsyncClient) -> None:
    app_id = await _submitted_application(client, "not-staff@example.com")
    tokens = await register_applicant(client, email="also-not-staff@example.com")
    headers = auth_headers(tokens)

    report = await client.post(
        f"/api/v1/applications/{app_id}/reports", headers=headers, json={"format": "pdf"}
    )
    assert report.status_code == 403

    analytics = await client.get("/api/v1/analytics", headers=headers)
    assert analytics.status_code == 403
