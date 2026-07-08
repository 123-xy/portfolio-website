from __future__ import annotations

import csv
import io
import json
from datetime import UTC, datetime

from ai_services.report_generator.contracts import (
    ApplicationReportData,
    BulkExportRow,
    DecisionRecord,
    EvidenceSummary,
    RiskSummary,
)
from ai_services.report_generator.csv_renderer import render_bulk_csv, render_csv
from ai_services.report_generator.json_renderer import render_bulk_json, render_json
from ai_services.report_generator.pdf_renderer import render_pdf


def _sample() -> ApplicationReportData:
    return ApplicationReportData(
        reference_no="APP-2026-000042",
        status="approved",
        loan_amount="₹22,00,000",
        loan_purpose="Home loan",
        co_applicant_name="Spouse Name",
        submitted_at=datetime(2026, 7, 8, 6, 0, tzinfo=UTC),
        decided_at=datetime(2026, 7, 8, 6, 10, tzinfo=UTC),
        risk=RiskSummary(
            score=0.12,
            band="low",
            recommendation="auto_approve_candidate",
            confidence=0.93,
            component_scores={"face_match": 0.95, "speech": 0.98},
            reasons=["Face match similarity 0.95", "Explicit consent detected"],
        ),
        evidence=EvidenceSummary(
            face_similarity=0.95, consent_status="explicit_yes", intent_aligned=True, fraud_score=0.05
        ),
        decisions=[
            DecisionRecord(
                decision="approve",
                reason="Evidence checks out.",
                created_at=datetime(2026, 7, 8, 6, 10, tzinfo=UTC),
            )
        ],
        generated_by="officer@verifyco.bank",
    )


def test_pdf_renders_nonempty_valid_pdf() -> None:
    pdf_bytes = render_pdf(_sample())
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1000


def test_pdf_handles_missing_risk_and_evidence() -> None:
    data = ApplicationReportData(
        reference_no="APP-2026-000043",
        status="draft",
        loan_amount="₹5,00,000",
        loan_purpose=None,
        co_applicant_name=None,
        submitted_at=None,
        decided_at=None,
        risk=None,
        evidence=None,
    )
    pdf_bytes = render_pdf(data)
    assert pdf_bytes.startswith(b"%PDF-")


def test_json_round_trips_key_fields() -> None:
    payload = json.loads(render_json(_sample()))
    assert payload["reference_no"] == "APP-2026-000042"
    assert payload["risk"]["band"] == "low"
    assert payload["decisions"][0]["decision"] == "approve"


def test_csv_has_header_and_one_data_row() -> None:
    rows = list(csv.reader(io.StringIO(render_csv(_sample()).decode("utf-8"))))
    assert rows[0][0] == "reference_no"
    assert rows[1][0] == "APP-2026-000042"
    assert rows[1][8] == "low"  # risk_band column


def test_bulk_csv_and_json_cover_all_rows() -> None:
    bulk_rows = [
        BulkExportRow(
            reference_no="APP-2026-000001",
            status="approved",
            loan_amount="₹5,00,000",
            co_applicant_name="A B",
            risk_band="low",
            risk_score=0.1,
            submitted_at=datetime(2026, 7, 1, tzinfo=UTC),
            decided_at=datetime(2026, 7, 2, tzinfo=UTC),
        ),
        BulkExportRow(
            reference_no="APP-2026-000002",
            status="rejected",
            loan_amount="₹8,00,000",
            co_applicant_name=None,
            risk_band="high",
            risk_score=0.9,
            submitted_at=datetime(2026, 7, 3, tzinfo=UTC),
            decided_at=None,
        ),
    ]
    csv_rows = list(csv.reader(io.StringIO(render_bulk_csv(bulk_rows).decode("utf-8"))))
    assert len(csv_rows) == 3  # header + 2 rows

    json_rows = json.loads(render_bulk_json(bulk_rows))
    assert len(json_rows) == 2
    assert json_rows[1]["co_applicant_name"] is None
