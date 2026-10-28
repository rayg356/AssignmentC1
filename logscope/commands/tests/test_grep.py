from datetime import datetime

from logscope.commands.grep_cmd import parse_since, run_grep


def test_grep_filters_by_level():
    lines = [
        "2026-10-01 09:00:00 INFO started\n",
        "2026-10-01 09:00:01 ERROR e1\n",
        "2026-10-01 09:00:02 WARN w1\n",
        "2026-10-01 09:00:03 ERROR e2\n",
    ]

    result = run_grep(lines, level="ERROR")

    assert [m.raw for m in result.matches] == [
        "2026-10-01 09:00:01 ERROR e1",
        "2026-10-01 09:00:03 ERROR e2",
    ]
    assert result.malformed_count == 0


def test_grep_filters_since_inclusive():
    lines = [
        "2026-10-01 08:59:59 ERROR old\n",
        "2026-10-01 09:00:00 ERROR keep1\n",
        "2026-10-01 09:00:01 ERROR keep2\n",
    ]

    since = datetime(2026, 10, 1, 9, 0)
    result = run_grep(lines, level="ERROR", since=since)

    assert [m.message for m in result.matches] == ["keep1", "keep2"]


def test_grep_counts_malformed_without_matching_them():
    lines = [
        "malformed line\n",
        "2026-10-01 09:00:00 ERROR ok\n",
        "2026-10-01 99:00:00 ERROR bad-ts\n",
    ]

    result = run_grep(lines, level="ERROR")

    assert [m.message for m in result.matches] == ["ok"]
    assert result.malformed_count == 2


def test_grep_invalid_level():
    try:
        run_grep([], level="DEBUG")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "invalid level" in str(exc)


def test_parse_since_strict_format():
    parsed = parse_since("2026-10-01 09:00")
    assert parsed == datetime(2026, 10, 1, 9, 0)

    try:
        parse_since("2026-10-01T09:00:00")
        assert False, "expected ValueError"
    except ValueError:
        pass
