from __future__ import annotations

import csv
import io

from ai_services.report_generator.contracts import ApplicationReportData, BulkExportRow


def _fmt(value: object) -> str:
    return "" if value is None else str(value)


def render_csv(data: ApplicationReportData) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "reference_no",
            "status",
            "loan_amount",
            "loan_purpose",
            "co_applicant_name",
            "submitted_at",
            "decided_at",
            "risk_score",
            "risk_band",
            "recommendation",
            "final_decision",
        ]
    )
    final_decision = data.decisions[0].decision if data.decisions else ""
    writer.writerow(
        [
            data.reference_no,
            data.status,
            data.loan_amount,
            _fmt(data.loan_purpose),
            _fmt(data.co_applicant_name),
            _fmt(data.submitted_at),
            _fmt(data.decided_at),
            _fmt(data.risk.score if data.risk else None),
            _fmt(data.risk.band if data.risk else None),
            _fmt(data.risk.recommendation if data.risk else None),
            final_decision,
        ]
    )
    return buffer.getvalue().encode("utf-8")


def render_bulk_csv(rows: list[BulkExportRow]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "reference_no",
            "status",
            "loan_amount",
            "co_applicant_name",
            "risk_band",
            "risk_score",
            "submitted_at",
            "decided_at",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row.reference_no,
                row.status,
                row.loan_amount,
                _fmt(row.co_applicant_name),
                _fmt(row.risk_band),
                _fmt(row.risk_score),
                _fmt(row.submitted_at),
                _fmt(row.decided_at),
            ]
        )
    return buffer.getvalue().encode("utf-8")
