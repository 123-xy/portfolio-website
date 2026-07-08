from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.ports.repositories.application_repository import ApplicationRepository
from app.domain.entities.application import Application as AppEntity
from app.domain.entities.application import Artifact as ArtifactEntity
from app.domain.entities.application import CoApplicant as CoApplicantEntity
from app.domain.value_objects.enums import ApplicationStatus
from app.infrastructure.db.models.application import Application as AppModel
from app.infrastructure.db.models.co_applicant import CoApplicant as CoApplicantModel


def _co_to_entity(model: CoApplicantModel | None) -> CoApplicantEntity | None:
    if model is None:
        return None
    return CoApplicantEntity(
        id=model.id,
        full_name=model.full_name,
        relationship_to_applicant=model.relationship_to_applicant,
        email=model.email,
        phone=model.phone,
    )


def _app_to_entity(model: AppModel, *, include_children: bool = True) -> AppEntity:
    artifacts: list[ArtifactEntity] = []
    co_applicant = None
    if include_children:
        co_applicant = _co_to_entity(model.co_applicant)
        artifacts = [
            ArtifactEntity(
                id=a.id,
                application_id=a.application_id,
                kind=a.kind.value,
                status=a.status.value,
                storage_key=a.storage_key,
                original_filename=a.original_filename,
                mime_type=a.mime_type,
                size_bytes=a.size_bytes,
                checksum_sha256=a.checksum_sha256,
            )
            for a in model.artifacts
        ]
    return AppEntity(
        id=model.id,
        reference_no=model.reference_no,
        applicant_id=model.applicant_id,
        loan_amount=model.loan_amount,
        status=model.status,
        loan_purpose=model.loan_purpose,
        submitted_at=model.submitted_at,
        decided_at=model.decided_at,
        created_at=model.created_at,
        co_applicant=co_applicant,
        artifacts=artifacts,
    )


class SqlAlchemyApplicationRepository(ApplicationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def next_reference_no(self) -> str:
        result = await self._session.execute(text("SELECT nextval('application_reference_seq')"))
        seq = int(result.scalar_one())
        year = datetime.now(UTC).year
        return f"APP-{year}-{seq:06d}"

    async def create(
        self,
        *,
        reference_no: str,
        applicant_id: uuid.UUID,
        loan_amount: Decimal,
        loan_purpose: str | None,
        co_applicant_full_name: str,
        co_applicant_relationship: str | None,
        co_applicant_email: str | None,
        co_applicant_phone: str | None,
    ) -> AppEntity:
        app = AppModel(
            reference_no=reference_no,
            applicant_id=applicant_id,
            loan_amount=loan_amount,
            loan_purpose=loan_purpose,
            status=ApplicationStatus.DRAFT,
        )
        app.co_applicant = CoApplicantModel(
            full_name=co_applicant_full_name,
            relationship_to_applicant=co_applicant_relationship,
            email=co_applicant_email,
            phone=co_applicant_phone,
        )
        self._session.add(app)
        await self._session.flush()
        # Children are freshly attached; build the entity directly.
        entity = _app_to_entity(app, include_children=False)
        entity.co_applicant = _co_to_entity(app.co_applicant)
        return entity

    async def get_by_id(self, application_id: uuid.UUID) -> AppEntity | None:
        result = await self._session.execute(
            select(AppModel)
            .where(AppModel.id == application_id)
            .options(selectinload(AppModel.co_applicant), selectinload(AppModel.artifacts))
        )
        model = result.scalar_one_or_none()
        return _app_to_entity(model) if model else None

    async def list_for_applicant(self, applicant_id: uuid.UUID) -> list[AppEntity]:
        result = await self._session.execute(
            select(AppModel)
            .where(AppModel.applicant_id == applicant_id)
            .options(selectinload(AppModel.co_applicant), selectinload(AppModel.artifacts))
            .order_by(AppModel.created_at.desc())
        )
        return [_app_to_entity(m) for m in result.scalars().all()]

    async def list_for_review(self) -> list[AppEntity]:
        result = await self._session.execute(
            select(AppModel)
            .where(AppModel.status == ApplicationStatus.PENDING_REVIEW)
            .options(selectinload(AppModel.co_applicant), selectinload(AppModel.artifacts))
            .order_by(AppModel.submitted_at.asc())
        )
        return [_app_to_entity(m) for m in result.scalars().all()]

    async def list_all(self) -> list[AppEntity]:
        result = await self._session.execute(
            select(AppModel)
            .options(selectinload(AppModel.co_applicant), selectinload(AppModel.artifacts))
            .order_by(AppModel.created_at.desc())
        )
        return [_app_to_entity(m) for m in result.scalars().all()]

    async def set_status(
        self,
        application_id: uuid.UUID,
        status: ApplicationStatus,
        *,
        mark_submitted: bool = False,
        mark_decided: bool = False,
    ) -> None:
        values: dict[str, object] = {"status": status}
        if mark_submitted:
            values["submitted_at"] = datetime.now(UTC)
        if mark_decided:
            values["decided_at"] = datetime.now(UTC)
        await self._session.execute(
            update(AppModel).where(AppModel.id == application_id).values(**values)
        )
