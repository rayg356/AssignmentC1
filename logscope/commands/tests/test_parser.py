from datetime import datetime

from logscope.parser import parse_log_line


def test_parse_valid_line():
    line = "2026-10-01 09:05:44 ERROR Database connection failed\n"

    result = parse_log_line(line)

    assert result.malformed is False
    assert result.reason is None
    assert result.record is not None
    assert result.record.timestamp == datetime(2026, 10, 1, 9, 5, 44)
    assert result.record.level == "ERROR"
    assert result.record.message == "Database connection failed"
    assert result.record.raw == "2026-10-01 09:05:44 ERROR Database connection failed"


def test_parse_line_with_invalid_timestamp():
    line = "2026-13-01 09:05:44 INFO bad month"

    result = parse_log_line(line)

    assert result.malformed is True
    assert result.record is None
    assert result.reason == "invalid timestamp"


def test_parse_line_with_invalid_level():
    line = "2026-10-01 09:05:44 DEBUG this level is not allowed"

    result = parse_log_line(line)

    assert result.malformed is True
    assert result.record is None
    assert result.reason == "unsupported level"


def test_parse_malformed_structure():
    line = "this is malformed"

    result = parse_log_line(line)

    assert result.malformed is True
    assert result.record is None
    assert result.reason == "line does not contain timestamp, level, and message"


def test_parse_empty_or_whitespace_line():
    assert parse_log_line("").malformed is True
    assert parse_log_line("   \t  ").malformed is True
    assert parse_log_line("\n").malformed is True
