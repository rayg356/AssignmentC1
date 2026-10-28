from datetime import datetime

from logscope.commands.summary import run_summary


def test_summary_counts_and_timestamps():
    lines = [
        "2026-10-01 09:00:00 INFO Application started\n",
        "2026-10-01 09:03:12 WARN Request took longer than expected\n",
        "2026-10-01 09:05:44 ERROR Database connection failed\n",
        "2026-10-01 09:05:45 ERROR Database connection failed\n",
        "malformed line\n",
    ]

    result = run_summary(lines)

    assert result.info_count == 1
    assert result.warn_count == 1
    assert result.error_count == 2
    assert result.malformed_count == 1
    assert result.first_timestamp == datetime(2026, 10, 1, 9, 0, 0)
    assert result.last_timestamp == datetime(2026, 10, 1, 9, 5, 45)
    assert result.top_errors == [("Database connection failed", 2)]


def test_summary_top_five_deterministic_tie_break():
    lines = [
        "2026-10-01 09:00:00 ERROR e3\n",
        "2026-10-01 09:00:01 ERROR e1\n",
        "2026-10-01 09:00:02 ERROR e2\n",
        "2026-10-01 09:00:03 ERROR e5\n",
        "2026-10-01 09:00:04 ERROR e4\n",
        "2026-10-01 09:00:05 ERROR e6\n",
    ]

    result = run_summary(lines)

    assert result.top_errors == [
        ("e1", 1),
        ("e2", 1),
        ("e3", 1),
        ("e4", 1),
        ("e5", 1),
    ]


def test_summary_empty_input():
    result = run_summary([])

    assert result.info_count == 0
    assert result.warn_count == 0
    assert result.error_count == 0
    assert result.top_errors == []
    assert result.first_timestamp is None
    assert result.last_timestamp is None
    assert result.malformed_count == 0


def test_summary_only_malformed():
    lines = ["bad\n", "\n", "2026-99-01 00:00:00 INFO x\n"]

    result = run_summary(lines)

    assert result.info_count == 0
    assert result.warn_count == 0
    assert result.error_count == 0
    assert result.top_errors == []
    assert result.first_timestamp is None
    assert result.last_timestamp is None
    assert result.malformed_count == 3
