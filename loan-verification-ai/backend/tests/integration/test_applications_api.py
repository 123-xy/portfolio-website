from __future__ import annotations

import httpx
import pytest

from tests.integration.conftest import FakePipelineDispatcher, register_applicant

pytestmark = pytest.mark.integration

_ARTIFACT_SPECS = [
    ("applicant_photo", "image/jpeg", "applicant.jpg", b"\xff\xd8\xff" + b"a" * 2048),
    ("coapplicant_photo", "image/jpeg", "coapplicant.jpg", b"\xff\xd8\xff" + b"b" * 2048),
    ("verification_video", "video/mp4", "video.mp4", b"\x00\x00\x00\x18ftypmp4" + b"c" * 8192),
]


async def _create_application(client: httpx.AsyncClient, headers: dict[str, str]) -> str:
    response = await client.post(
        "/api/v1/applications",
        headers=headers,
        json={
            "loan_amount": 1500000,
            "loan_purpose": "Home renovation",
            "co_applicant": {
                "full_name": "Co Applicant",
                "relationship": "sibling",
                "phone": "+919876543210",
            },
        },
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


async def _upload_all_artifacts(
    client: httpx.AsyncClient, headers: dict[str, str], application_id: str
) -> None:
    for kind, content_type, filename, payload in _ARTIFACT_SPECS:
        init = await client.post(
            f"/api/v1/applications/{application_id}/uploads/init",
            headers=headers,
            json={"kind": kind, "content_type": content_type, "filename": filename},
        )
        assert init.status_code == 200, init.text
        ticket = init.json()

        put = await httpx.AsyncClient().put(
            ticket["upload_url"], content=payload, headers={"Content-Type": content_type}
        )
        assert put.status_code in (200, 204), put.text

        confirm = await client.post(
            f"/api/v1/applications/{application_id}/uploads/confirm",
            headers=headers,
            json={"artifact_id": ticket["artifact_id"]},
        )
        assert confirm.status_code == 200, confirm.text
        assert confirm.json()["status"] == "uploaded"


async def test_full_application_lifecycle_create_upload_submit(
    client: httpx.AsyncClient, fake_dispatcher: FakePipelineDispatcher
) -> None:
    tokens = await register_applicant(client, email="applicant1@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    app_id = await _create_application(client, headers)
    detail = await client.get(f"/api/v1/applications/{app_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["status"] == "draft"

    await _upload_all_artifacts(client, headers, app_id)

    submitted = await client.post(f"/api/v1/applications/{app_id}/submit", headers=headers)
    assert submitted.status_code == 200, submitted.text
    body = submitted.json()
    assert body["status"] == "submitted"
    assert body["submitted_at"] is not None
    assert len(body["artifacts"]) == 3

    # The AI pipeline was enqueued (dispatch port called), without needing a
    # real Celery worker for this API-level test.
    assert str(app_id) in [str(a) for a in fake_dispatcher.dispatched]

    listed = await client.get("/api/v1/applications", headers=headers)
    assert listed.status_code == 200
    assert any(a["id"] == app_id for a in listed.json())


async def test_submit_fails_when_a_required_artifact_is_missing(client: httpx.AsyncClient) -> None:
    tokens = await register_applicant(client, email="applicant2@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    app_id = await _create_application(client, headers)

    # Upload only the first two of the three required kinds.
    for kind, content_type, filename, payload in _ARTIFACT_SPECS[:2]:
        init = await client.post(
            f"/api/v1/applications/{app_id}/uploads/init",
            headers=headers,
            json={"kind": kind, "content_type": content_type, "filename": filename},
        )
        ticket = init.json()
        await httpx.AsyncClient().put(
            ticket["upload_url"], content=payload, headers={"Content-Type": content_type}
        )
        await client.post(
            f"/api/v1/applications/{app_id}/uploads/confirm",
            headers=headers,
            json={"artifact_id": ticket["artifact_id"]},
        )

    submitted = await client.post(f"/api/v1/applications/{app_id}/submit", headers=headers)
    assert submitted.status_code == 422
    assert "verification_video" in submitted.json()["error"]["message"]


async def test_applicant_cannot_view_or_upload_to_another_applicants_application(
    client: httpx.AsyncClient,
) -> None:
    owner_tokens = await register_applicant(client, email="owner@example.com")
    owner_headers = {"Authorization": f"Bearer {owner_tokens['access_token']}"}
    app_id = await _create_application(client, owner_headers)

    stranger_tokens = await register_applicant(client, email="stranger@example.com")
    stranger_headers = {"Authorization": f"Bearer {stranger_tokens['access_token']}"}

    # 404, not 403 — existence of another applicant's record is not confirmed.
    get_response = await client.get(f"/api/v1/applications/{app_id}", headers=stranger_headers)
    assert get_response.status_code == 404

    init_response = await client.post(
        f"/api/v1/applications/{app_id}/uploads/init",
        headers=stranger_headers,
        json={"kind": "applicant_photo", "content_type": "image/jpeg", "filename": "x.jpg"},
    )
    assert init_response.status_code == 404


async def test_unauthenticated_request_is_rejected(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/applications", json={"loan_amount": 100000, "loan_purpose": "x"}
    )
    assert response.status_code == 401
