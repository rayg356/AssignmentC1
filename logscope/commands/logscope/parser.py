from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


VALID_LEVELS = {"INFO", "WARN", "ERROR"}
_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True)
class LogRecord:
    timestamp: datetime
    level: str
    message: str
    raw: str


@dataclass(frozen=True)
class ParseResult:
    record: Optional[LogRecord]
    malformed: bool
    reason: Optional[str] = None


def parse_log_line(line: str) -> ParseResult:
    """
    Parse one log line in format:
    YYYY-MM-DD HH:mm:ss LEVEL message
    """
    raw = line.rstrip("\r\n")

    if not raw.strip():
        return ParseResult(record=None, malformed=True, reason="empty line")

    parts = raw.split(" ", 3)
    if len(parts) != 4:
        return ParseResult(
            record=None,
            malformed=True,
            reason="line does not contain timestamp, level, and message",
        )

    date_part, time_part, level, message = parts
    timestamp_text = f"{date_part} {time_part}"

    try:
        timestamp = datetime.strptime(timestamp_text, _TIMESTAMP_FORMAT)
    except ValueError:
        return ParseResult(record=None, malformed=True, reason="invalid timestamp")

    if level not in VALID_LEVELS:
        return ParseResult(record=None, malformed=True, reason="unsupported level")

    if not message:
        return ParseResult(record=None, malformed=True, reason="empty message")

    return ParseResult(
        record=LogRecord(
            timestamp=timestamp,
            level=level,
            message=message,
            raw=raw,
        ),
        malformed=False,
        reason=None,
    )
