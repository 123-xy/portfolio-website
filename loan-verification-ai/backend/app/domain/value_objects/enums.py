"""Closed value sets shared by the domain and persisted as PostgreSQL ENUMs.

Defining them once here (as Python enums) and referencing them from the ORM
models keeps the DB enum and the domain in lockstep — a new status is added in
exactly one place.
"""

from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    OFFICER = "officer"
    APPLICANT = "applicant"
    AUDITOR = "auditor"


class ApplicationStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    PENDING_REVIEW = "pending_review"
    NEEDS_ATTENTION = "needs_attention"
    MORE_INFO_REQUESTED = "more_info_requested"
    APPROVED = "approved"
    REJECTED = "rejected"


class ArtifactKind(StrEnum):
    APPLICANT_PHOTO = "applicant_photo"
    COAPPLICANT_PHOTO = "coapplicant_photo"
    VERIFICATION_VIDEO = "verification_video"
    DOCUMENT = "document"


class ArtifactStatus(StrEnum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    INGESTED = "ingested"
    VALIDATED = "validated"
    REJECTED = "rejected"
    PURGED = "purged"


class VerificationStage(StrEnum):
    INGEST = "ingest"
    FRAME_EXTRACTION = "frame_extraction"
    FACE_DETECTION = "face_detection"
    FACE_EMBEDDING = "face_embedding"
    FACE_MATCH = "face_match"
    AUDIO_EXTRACTION = "audio_extraction"
    TRANSCRIPTION = "transcription"
    CONSENT_DETECTION = "consent_detection"
    INTENT_ANALYSIS = "intent_analysis"
    FRAUD_CHECK = "fraud_check"
    RISK_SCORING = "risk_scoring"


class StageStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class RiskBand(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Recommendation(StrEnum):
    AUTO_APPROVE_CANDIDATE = "auto_approve_candidate"
    NEEDS_REVIEW = "needs_review"
    HIGH_RISK_REJECT_CANDIDATE = "high_risk_reject_candidate"


class ConsentStatus(StrEnum):
    EXPLICIT_YES = "explicit_yes"
    AMBIGUOUS = "ambiguous"
    EXPLICIT_NO = "explicit_no"
    NOT_DETECTED = "not_detected"


class DecisionType(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_MORE_INFO = "request_more_info"


class ReportFormat(StrEnum):
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"


class NotificationChannel(StrEnum):
    IN_APP = "in_app"
    EMAIL = "email"


class AuditAction(StrEnum):
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_LOGIN_FAILED = "user_login_failed"
    APPLICATION_CREATED = "application_created"
    ARTIFACT_UPLOADED = "artifact_uploaded"
    ARTIFACT_VIEWED = "artifact_viewed"
    ARTIFACT_PURGED = "artifact_purged"
    PIPELINE_STAGE_COMPLETED = "pipeline_stage_completed"
    PIPELINE_STAGE_FAILED = "pipeline_stage_failed"
    RISK_SCORED = "risk_scored"
    OFFICER_DECISION = "officer_decision"
    REPORT_GENERATED = "report_generated"
    REPORT_EXPORTED = "report_exported"
    RETENTION_PURGE = "retention_purge"
    ROLE_CHANGED = "role_changed"
