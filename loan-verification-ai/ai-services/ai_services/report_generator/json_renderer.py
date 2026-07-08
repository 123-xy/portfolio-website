from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date, datetime

from ai_services.report_generator.contracts import ApplicationReportData, BulkExportRow


def _default(value: object) -> str:
    if isinstance(value, datetime | date):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def render_json(data: ApplicationReportData) -> bytes:
    return json.dumps(asdict(data), default=_default, indent=2).encode("utf-8")


def render_bulk_json(rows: list[BulkExportRow]) -> bytes:
    return json.dumps([asdict(r) for r in rows], default=_default, indent=2).encode("utf-8")
