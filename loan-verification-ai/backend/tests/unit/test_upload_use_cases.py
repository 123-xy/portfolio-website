from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.application.dto.applications import (
    ConfirmUploadCommand,
    CreateApplicationCommand,
    InitUploadCommand,
)
from app.application.ports.repositories.application_repository import ApplicationRepository
from app.application.ports.repositories.artifact_repository import ArtifactRepository
from app.application.ports.services.object_storage import ObjectStat, ObjectStorage
from app.application.ports.services.pipeline import PipelineDispatcher
from app.application.use_cases.applications.create_application import CreateApplication
from app.application.use_cases.applications.query_applications import GetApplication
from app.application.use_cases.applications.submit_application import SubmitApplication
from app.application.use_cases.applications.upload_artifact import (
    ConfirmArtifactUpload,
    InitArtifactUpload,
)
from app.domain.entities.application import Application, Artifact, CoApplicant
from app.domain.exceptions import NotFoundError, ValidationError
from app.domain.value_objects.enums import ApplicationStatus, ArtifactKind, UserRole


class FakeAppRepo(ApplicationRepository):
    def __init__(self) -> None:
        self.apps: dict[uuid.UUID, Application] = {}
        self._seq = 0

    async def next_reference_no(self) -> str:
        self._seq += 1
        return f"APP-2026-{self._seq:06d}"

    async def create(self, **kw) -> Application:
        app = Application(
            id=uuid.uuid4(),
            reference_no=kw["reference_no"],
            applicant_id=kw["applicant_id"],
            loan_amount=kw["loan_amount"],
            status=ApplicationStatus.DRAFT,
            loan_purpose=kw["loan_purpose"],
            co_applicant=CoApplicant(id=uuid.uuid4(), full_name=kw["co_applicant_full_name"]),
        )
        self.apps[app.id] = app
        return app

    async def get_by_id(self, application_id: uuid.UUID) -> Application | None:
        return self.apps.get(application_id)

    async def list_for_applicant(self, applicant_id: uuid.UUID) -> list[Application]:
        return [a for a in self.apps.values() if a.applicant_id == applicant_id]

    async def list_for_review(self) -> list[Application]:
        return [a for a in self.apps.values() if a.status == ApplicationStatus.PENDING_REVIEW]

    async def set_status(self, application_id, status, *, mark_submitted=False) -> None:
        self.apps[application_id].status = status


class FakeArtifactRepo(ArtifactRepository):
    def __init__(self) -> None:
        self.artifacts: dict[uuid.UUID, Artifact] = {}
        self.rejected_kinds: list[ArtifactKind] = []

    async def create_pending(self, **kw) -> Artifact:
        art = Artifact(
            id=kw["artifact_id"],
            application_id=kw["application_id"],
            kind=kw["kind"].value,
            status="pending",
            storage_key=kw["storage_key"],
            mime_type=kw["mime_type"],
            original_filename=kw["original_filename"],
        )
        self.artifacts[art.id] = art
        return art

    async def get_by_id(self, artifact_id: uuid.UUID) -> Artifact | None:
        return self.artifacts.get(artifact_id)

    async def mark_uploaded(self, artifact_id, *, size_bytes, checksum_sha256) -> None:
        art = self.artifacts[artifact_id]
        art.status = "uploaded"
        art.size_bytes = size_bytes
        art.checksum_sha256 = checksum_sha256

    async def reject_existing_singletons(self, application_id, kind) -> None:
        self.rejected_kinds.append(kind)

    async def checksum_seen_on_other_application(self, checksum, exclude_application_id) -> bool:
        return False


class FakeStorage(ObjectStorage):
    def __init__(self, stat: ObjectStat | None = None) -> None:
        self._stat = stat
        self.deleted: list[str] = []

    async def ensure_bucket(self) -> None:  # pragma: no cover
        pass

    async def create_upload_url(self, key, *, content_type, expires_seconds=900) -> str:
        return f"https://storage.local/{key}?signed=1"

    async def create_download_url(self, key, *, expires_seconds=300) -> str:  # pragma: no cover
        return f"https://storage.local/{key}?download=1"

    async def stat(self, key: str) -> ObjectStat | None:
        return self._stat

    async def download_bytes(self, key: str) -> bytes:  # pragma: no cover
        return b""

    async def delete(self, key: str) -> None:
        self.deleted.append(key)


class FakeDispatcher(PipelineDispatcher):
    def __init__(self) -> None:
        self.dispatched: list[uuid.UUID] = []

    def dispatch(self, application_id) -> None:
        self.dispatched.append(application_id)


async def _new_draft(apps: FakeAppRepo, owner: uuid.UUID) -> Application:
    return await CreateApplication(apps).execute(
        CreateApplicationCommand(
            applicant_id=owner,
            loan_amount=Decimal("100000"),
            loan_purpose=None,
            co_applicant_full_name="Co Applicant",
            co_applicant_relationship=None,
            co_applicant_email=None,
            co_applicant_phone=None,
        )
    )


async def test_reference_number_format() -> None:
    apps = FakeAppRepo()
    app = await _new_draft(apps, uuid.uuid4())
    assert app.reference_no == "APP-2026-000001"


async def test_init_upload_rejects_disallowed_content_type() -> None:
    apps, arts, storage = FakeAppRepo(), FakeArtifactRepo(), FakeStorage()
    owner = uuid.uuid4()
    app = await _new_draft(apps, owner)
    use_case = InitArtifactUpload(apps, arts, storage)
    with pytest.raises(ValidationError):
        await use_case.execute(
            InitUploadCommand(app.id, "applicant_photo", "application/x-msdownload", None),
            owner,
            UserRole.APPLICANT,
        )


async def test_init_upload_supersedes_prior_singleton_and_returns_ticket() -> None:
    apps, arts, storage = FakeAppRepo(), FakeArtifactRepo(), FakeStorage()
    owner = uuid.uuid4()
    app = await _new_draft(apps, owner)
    ticket = await InitArtifactUpload(apps, arts, storage).execute(
        InitUploadCommand(app.id, "applicant_photo", "image/jpeg", "me.jpg"),
        owner,
        UserRole.APPLICANT,
    )
    assert ticket.upload_url.startswith("https://storage.local/")
    assert ArtifactKind.APPLICANT_PHOTO in arts.rejected_kinds
    assert arts.artifacts[ticket.artifact_id].status == "pending"


async def test_confirm_upload_enforces_size_limit_and_deletes() -> None:
    apps, arts = FakeAppRepo(), FakeArtifactRepo()
    owner = uuid.uuid4()
    app = await _new_draft(apps, owner)
    # 20 MB object exceeds the 10 MB photo limit.
    storage = FakeStorage(stat=ObjectStat(size_bytes=20 * 1024 * 1024, etag="abc"))
    ticket = await InitArtifactUpload(apps, arts, storage).execute(
        InitUploadCommand(app.id, "applicant_photo", "image/jpeg", None), owner, UserRole.APPLICANT
    )
    with pytest.raises(ValidationError):
        await ConfirmArtifactUpload(apps, arts, storage).execute(
            ConfirmUploadCommand(app.id, ticket.artifact_id), owner, UserRole.APPLICANT
        )
    assert storage.deleted  # oversized object was removed


async def test_confirm_upload_marks_uploaded() -> None:
    apps, arts = FakeAppRepo(), FakeArtifactRepo()
    owner = uuid.uuid4()
    app = await _new_draft(apps, owner)
    storage = FakeStorage(stat=ObjectStat(size_bytes=1234, etag="etag123"))
    ticket = await InitArtifactUpload(apps, arts, storage).execute(
        InitUploadCommand(app.id, "applicant_photo", "image/jpeg", None), owner, UserRole.APPLICANT
    )
    artifact = await ConfirmArtifactUpload(apps, arts, storage).execute(
        ConfirmUploadCommand(app.id, ticket.artifact_id), owner, UserRole.APPLICANT
    )
    assert artifact.status == "uploaded"
    assert artifact.size_bytes == 1234
    assert artifact.checksum_sha256 == "etag123"


async def test_submit_requires_all_artifacts() -> None:
    apps = FakeAppRepo()
    owner = uuid.uuid4()
    app = await _new_draft(apps, owner)
    with pytest.raises(ValidationError):
        await SubmitApplication(apps, FakeDispatcher()).execute(app.id, owner, UserRole.APPLICANT)


async def test_submit_succeeds_when_required_present() -> None:
    apps = FakeAppRepo()
    owner = uuid.uuid4()
    app = await _new_draft(apps, owner)
    for kind in ("applicant_photo", "coapplicant_photo", "verification_video"):
        app.artifacts.append(
            Artifact(
                id=uuid.uuid4(),
                application_id=app.id,
                kind=kind,
                status="uploaded",
                storage_key=f"k/{kind}",
            )
        )
    result = await SubmitApplication(apps, FakeDispatcher()).execute(
        app.id, owner, UserRole.APPLICANT
    )
    assert result.status is ApplicationStatus.SUBMITTED
    assert result.submitted_at is not None


async def test_get_application_hides_other_applicants() -> None:
    apps = FakeAppRepo()
    owner, stranger = uuid.uuid4(), uuid.uuid4()
    app = await _new_draft(apps, owner)
    with pytest.raises(NotFoundError):
        await GetApplication(apps).execute(app.id, stranger, UserRole.APPLICANT)
    # An officer, by contrast, may view it.
    seen = await GetApplication(apps).execute(app.id, stranger, UserRole.OFFICER)
    assert seen.id == app.id
