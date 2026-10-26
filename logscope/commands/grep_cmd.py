from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from logscope.parser import VALID_LEVELS, parse_log_line


@dataclass(frozen=True)
class GrepMatch:
    timestamp: datetime
    level: str
    message: str
    raw: str


@dataclass(frozen=True)
class GrepResult:
    matches: list[GrepMatch]
    malformed_count: int


def parse_since(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M")


def run_grep(lines: Iterable[str], level: str, since: datetime | None = None) -> GrepResult:
    if level not in VALID_LEVELS:
        raise ValueError("invalid level")

    malformed_count = 0
    matches: list[GrepMatch] = []

    for line in lines:
        parsed = parse_log_line(line)
        if parsed.malformed:
            malformed_count += 1
            continue

        record = parsed.record
        if record is None:
            malformed_count += 1
            continue

        if record.level != level:
            continue

        if since is not None and record.timestamp < since:
            continue

        matches.append(
            GrepMatch(
                timestamp=record.timestamp,
                level=record.level,
                message=record.message,
                raw=record.raw,
            )
        )

    return GrepResult(matches=matches, malformed_count=malformed_count)


def grep_to_payload(result: GrepResult) -> dict[str, object]:
    return {
        "matches": [
            {
                "timestamp": match.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "level": match.level,
                "message": match.message,
                "raw": match.raw,
            }
            for match in result.matches
        ],
        "malformed_count": result.malformed_count,
    }


def render_grep_text(result: GrepResult) -> str:
    lines = [match.raw for match in result.matches]
    lines.append(f"Malformed lines: {result.malformed_count}")
    return "\n".join(lines)
