from logscope.commands.timeline import render_timeline_text, run_timeline


def test_timeline_15m_bucket_alignment_and_counts():
    lines = [
        "2026-10-01 09:00:01 ERROR e1\n",
        "2026-10-01 09:14:59 ERROR e2\n",
        "2026-10-01 09:15:00 ERROR e3\n",
        "2026-10-01 09:29:59 ERROR e4\n",
        "2026-10-01 09:30:00 INFO not-counted\n",
        "malformed\n",
    ]

    result = run_timeline(lines, bucket="15m")

    assert result.malformed_count == 1
    assert len(result.buckets) == 3
    assert result.buckets[0].start.strftime("%H:%M") == "09:00"
    assert result.buckets[0].error_count == 2
    assert result.buckets[1].start.strftime("%H:%M") == "09:15"
    assert result.buckets[1].error_count == 2
    assert result.buckets[2].start.strftime("%H:%M") == "09:30"
    assert result.buckets[2].error_count == 0


def test_timeline_invalid_bucket():
    try:
        run_timeline([], bucket="30m")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "invalid bucket" in str(exc)


def test_timeline_empty_input():
    result = run_timeline([], bucket="15m")
    assert result.buckets == []
    assert result.malformed_count == 0


def test_timeline_text_output_is_deterministic():
    lines = [
        "2026-10-01 09:00:00 ERROR e1\n",
        "2026-10-01 09:15:00 ERROR e2\n",
    ]
    result = run_timeline(lines)
    rendered = render_timeline_text(result, width=10)

    assert "Bucket: 15m" in rendered
    assert "2026-10-01 09:00 | ########## (1)" in rendered
    assert "2026-10-01 09:15 | ########## (1)" in rendered
    assert "Malformed lines: 0" in rendered
