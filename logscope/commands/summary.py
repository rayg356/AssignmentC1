from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from logscope.parser import parse_log_line


@dataclass(frozen=True)
class SummaryResult:
    info_count: int
    warn_count: int
    error_count: int
    top_errors: list[tuple[str, int]]
    first_timestamp: datetime | None
    last_timestamp: datetime | None
    malformed_count: int


def run_summary(lines: Iterable[str]) -> SummaryResult:
    info_count = 0
    warn_count = 0
    error_count = 0
    malformed_count = 0
    error_messages: Counter[str] = Counter()
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None

    for line in lines:
        parsed = parse_log_line(line)
        if parsed.malformed:
            malformed_count += 1
            continue

        record = parsed.record
        if record is None:
            malformed_count += 1
            continue

        if first_timestamp is None or record.timestamp < first_timestamp:
            first_timestamp = record.timestamp
        if last_timestamp is None or record.timestamp > last_timestamp:
            last_timestamp = record.timestamp

        if record.level == "INFO":
            info_count += 1
        elif record.level == "WARN":
            warn_count += 1
        elif record.level == "ERROR":
            error_count += 1
            error_messages[record.message] += 1

    top_errors = sorted(
        error_messages.items(),
        key=lambda item: (-item[1], item[0]),
    )[:5]

    return SummaryResult(
        info_count=info_count,
        warn_count=warn_count,
        error_count=error_count,
        top_errors=top_errors,
        first_timestamp=first_timestamp,
        last_timestamp=last_timestamp,
        malformed_count=malformed_count,
    )


def summary_to_payload(result: SummaryResult) -> dict[str, object]:
    return {
        "info_count": result.info_count,
        "warn_count": result.warn_count,
        "error_count": result.error_count,
        "top_errors": [
            {"message": message, "count": count}
            for message, count in result.top_errors
        ],
        "first_timestamp": (
            result.first_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if result.first_timestamp is not None
            else None
        ),
        "last_timestamp": (
            result.last_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if result.last_timestamp is not None
            else None
        ),
        "malformed_count": result.malformed_count,
    }


def render_summary_text(result: SummaryResult) -> str:
    lines = [
        f"INFO: {result.info_count}",
        f"WARN: {result.warn_count}",
        f"ERROR: {result.error_count}",
        "First timestamp: "
        + (
            result.first_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if result.first_timestamp is not None
            else "N/A"
        ),
        "Last timestamp: "
        + (
            result.last_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if result.last_timestamp is not None
            else "N/A"
        ),
        f"Malformed lines: {result.malformed_count}",
        "Top 5 error messages:",
    ]

    if not result.top_errors:
        lines.append("- None")
    else:
        for message, count in result.top_errors:
            lines.append(f"- {message}: {count}")

    return "\n".join(lines)
