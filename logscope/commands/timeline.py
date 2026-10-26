from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from logscope.parser import parse_log_line


@dataclass(frozen=True)
class TimelineBucket:
    start: datetime
    error_count: int


@dataclass(frozen=True)
class TimelineResult:
    bucket: str
    buckets: list[TimelineBucket]
    malformed_count: int


def _align_to_15m(ts: datetime) -> datetime:
    minute = (ts.minute // 15) * 15
    return ts.replace(minute=minute, second=0, microsecond=0)


def _iter_15m_range(start: datetime, end: datetime):
    current = start
    step = timedelta(minutes=15)
    while current <= end:
        yield current
        current += step


def run_timeline(lines: Iterable[str], bucket: str = "15m") -> TimelineResult:
    if bucket != "15m":
        raise ValueError("invalid bucket: only '15m' is supported")

    malformed_count = 0
    counts: dict[datetime, int] = {}
    min_ts: datetime | None = None
    max_ts: datetime | None = None

    for line in lines:
        parsed = parse_log_line(line)
        if parsed.malformed:
            malformed_count += 1
            continue

        record = parsed.record
        if record is None:
            malformed_count += 1
            continue

        if min_ts is None or record.timestamp < min_ts:
            min_ts = record.timestamp
        if max_ts is None or record.timestamp > max_ts:
            max_ts = record.timestamp

        if record.level == "ERROR":
            bucket_start = _align_to_15m(record.timestamp)
            counts[bucket_start] = counts.get(bucket_start, 0) + 1

    if min_ts is None or max_ts is None:
        return TimelineResult(bucket=bucket, buckets=[], malformed_count=malformed_count)

    start = _align_to_15m(min_ts)
    end = _align_to_15m(max_ts)

    ordered = [
        TimelineBucket(start=slot, error_count=counts.get(slot, 0))
        for slot in _iter_15m_range(start, end)
    ]

    return TimelineResult(
        bucket=bucket,
        buckets=ordered,
        malformed_count=malformed_count,
    )


def render_timeline_text(result: TimelineResult, width: int = 40) -> str:
    lines: list[str] = []
    lines.append(f"Bucket: {result.bucket}")
    lines.append("ERROR timeline:")

    if not result.buckets:
        lines.append("- None")
        lines.append(f"Malformed lines: {result.malformed_count}")
        return "\n".join(lines)

    max_count = max(bucket.error_count for bucket in result.buckets)
    for bucket in result.buckets:
        label = bucket.start.strftime("%Y-%m-%d %H:%M")
        if max_count == 0:
            bar = ""
        else:
            bar_len = int((bucket.error_count / max_count) * width)
            bar = "#" * bar_len
        lines.append(f"{label} | {bar} ({bucket.error_count})")

    lines.append(f"Malformed lines: {result.malformed_count}")
    return "\n".join(lines)
