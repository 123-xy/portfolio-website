import uuid
from datetime import UTC, datetime

import pytest

from app.core.config import Settings
from app.domain.exceptions import AuthenticationError
from app.domain.value_objects.enums import UserRole
from app.infrastructure.auth.token_service import JwtTokenService


def _service() -> JwtTokenService:
    return JwtTokenService(Settings(jwt_secret_key="unit-test-secret-key-abcdefghijklmnop"))


def test_access_token_round_trips_claims() -> None:
    service = _service()
    user_id = uuid.uuid4()
    token = service.create_access_token(user_id, UserRole.OFFICER)

    claims = service.decode_access_token(token)
    assert claims.user_id == user_id
    assert claims.role is UserRole.OFFICER
    assert claims.token_id  # jti present


def test_decode_rejects_tampered_token() -> None:
    service = _service()
    token = service.create_access_token(uuid.uuid4(), UserRole.APPLICANT)
    with pytest.raises(AuthenticationError):
        service.decode_access_token(token + "tampered")


def test_decode_rejects_token_signed_with_other_secret() -> None:
    issuer = JwtTokenService(Settings(jwt_secret_key="secret-one-aaaaaaaaaaaaaaaaaaaa"))
    verifier = JwtTokenService(Settings(jwt_secret_key="secret-two-bbbbbbbbbbbbbbbbbbbb"))
    token = issuer.create_access_token(uuid.uuid4(), UserRole.ADMIN)
    with pytest.raises(AuthenticationError):
        verifier.decode_access_token(token)


def test_refresh_token_hash_is_deterministic_and_matches() -> None:
    service = _service()
    material = service.create_refresh_token()
    assert material.token_hash == service.hash_refresh_token(material.raw)
    assert material.expires_at > datetime.now(UTC)
    # Raw token is high-entropy; the hash never equals the raw value.
    assert material.token_hash != material.raw
