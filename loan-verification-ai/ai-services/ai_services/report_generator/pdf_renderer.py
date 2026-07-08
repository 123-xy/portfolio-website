"""PDF rendering via reportlab — a real, pure-Python renderer (no native or
model dependencies), producing a genuine multi-section compliance document:
loan details, risk breakdown, evidence summary, and decision history.
"""

from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from ai_services.report_generator.contracts import ApplicationReportData

_STYLES = getSampleStyleSheet()
_TITLE = ParagraphStyle("ReportTitle", parent=_STYLES["Title"], fontSize=18, spaceAfter=4)
_SECTION = ParagraphStyle(
    "SectionHeading", parent=_STYLES["Heading2"], spaceBefore=14, spaceAfter=6
)
_BODY = _STYLES["BodyText"]
_MUTED = ParagraphStyle("Muted", parent=_BODY, textColor=colors.grey, fontSize=9)


def _kv_table(rows: list[tuple[str, str]]) -> Table:
    table = Table(rows, colWidths=[45 * mm, 110 * mm])
    table.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.whitesmoke),
            ]
        )
    )
    return table


def _fmt_dt(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%d %H:%M UTC") if value else "—"


def render_pdf(data: ApplicationReportData) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        title=f"Verification Report — {data.reference_no}",
    )

    story: list[Flowable] = [
        Paragraph("Co-Applicant Verification Report", _TITLE),
        Paragraph(f"Reference {data.reference_no} · Status {data.status.upper()}", _MUTED),
        Spacer(1, 10),
        Paragraph("Loan Details", _SECTION),
        _kv_table(
            [
                ("Amount", data.loan_amount),
                ("Purpose", data.loan_purpose or "—"),
                ("Co-applicant", data.co_applicant_name or "—"),
                ("Submitted", _fmt_dt(data.submitted_at)),
                ("Decided", _fmt_dt(data.decided_at)),
            ]
        ),
    ]

    if data.risk is not None:
        story.append(Paragraph("Risk Assessment", _SECTION))
        story.append(
            _kv_table(
                [
                    ("Risk score", f"{data.risk.score:.2f} ({data.risk.band})"),
                    ("Recommendation", data.risk.recommendation.replace("_", " ")),
                    ("Confidence", f"{data.risk.confidence:.0%}"),
                    (
                        "Components",
                        ", ".join(f"{k}: {v:.0%}" for k, v in data.risk.component_scores.items()),
                    ),
                ]
            )
        )
        if data.risk.reasons:
            story.append(Spacer(1, 6))
            for reason in data.risk.reasons:
                story.append(Paragraph(f"• {reason}", _BODY))

    if data.evidence is not None:
        story.append(Paragraph("Evidence Summary", _SECTION))
        story.append(
            _kv_table(
                [
                    (
                        "Face match",
                        f"{data.evidence.face_similarity:.2f}"
                        if data.evidence.face_similarity is not None
                        else "—",
                    ),
                    ("Consent", data.evidence.consent_status or "—"),
                    (
                        "Intent aligned",
                        "Yes"
                        if data.evidence.intent_aligned
                        else ("No" if data.evidence.intent_aligned is False else "—"),
                    ),
                    (
                        "Fraud score",
                        f"{data.evidence.fraud_score:.2f}"
                        if data.evidence.fraud_score is not None
                        else "—",
                    ),
                ]
            )
        )

    story.append(Paragraph("Decision History", _SECTION))
    if data.decisions:
        rows = [["Decision", "Reason", "Timestamp"]]
        for d in data.decisions:
            rows.append([d.decision.replace("_", " "), d.reason, _fmt_dt(d.created_at)])
        history_table = Table(rows, colWidths=[30 * mm, 90 * mm, 35 * mm])
        history_table.setStyle(
            TableStyle(
                [
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.whitesmoke),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(history_table)
    else:
        story.append(Paragraph("No decision has been recorded yet.", _BODY))

    story.append(Spacer(1, 16))
    story.append(
        Paragraph(
            f"Generated {_fmt_dt(data.generated_at)} by {data.generated_by or 'system'}.",
            _MUTED,
        )
    )

    doc.build(story)
    return buffer.getvalue()
