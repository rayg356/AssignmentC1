import json
from pathlib import Path

from logscope.commands.grep_cmd import grep_to_payload, run_grep
from logscope.commands.summary import run_summary, summary_to_payload
from logscope.commands.timeline import run_timeline, timeline_to_payload
from logscope.renderers import markdown_report_path, to_json, write_markdown_report


def test_summary_json_payload_and_encoding_stable():
    result = run_summary(
        [
            "2026-10-01 09:00:00 INFO started\n",
            "2026-10-01 09:00:01 ERROR e1\n",
            "bad\n",
        ]
    )
    payload = summary_to_payload(result)
    encoded = to_json(payload)
    decoded = json.loads(encoded)

    assert decoded["info_count"] == 1
    assert decoded["error_count"] == 1
    assert decoded["malformed_count"] == 1
    assert decoded["top_errors"] == [{"message": "e1", "count": 1}]


def test_timeline_json_payload_contains_buckets():
    result = run_timeline(
        [
            "2026-10-01 09:00:00 ERROR e1\n",
            "2026-10-01 09:15:00 ERROR e2\n",
        ]
    )
    payload = timeline_to_payload(result)

    assert payload["bucket"] == "15m"
    assert payload["malformed_count"] == 0
    assert payload["buckets"] == [
        {"start": "2026-10-01 09:00", "error_count": 1},
        {"start": "2026-10-01 09:15", "error_count": 1},
    ]


def test_grep_json_payload_contains_matches():
    result = run_grep(
        [
            "2026-10-01 09:00:00 ERROR e1\n",
            "2026-10-01 09:00:01 WARN w1\n",
        ],
        level="ERROR",
    )
    payload = grep_to_payload(result)

    assert payload["malformed_count"] == 0
    assert payload["matches"] == [
        {
            "timestamp": "2026-10-01 09:00:00",
            "level": "ERROR",
            "message": "e1",
            "raw": "2026-10-01 09:00:00 ERROR e1",
        }
    ]


def test_markdown_report_written_and_path_printable(tmp_path: Path):
    logfile = tmp_path / "app.log"
    logfile.write_text("2026-10-01 09:00:00 INFO started\n", encoding="utf-8")
    payload = {"malformed_count": 0, "items": ["a", "b"]}

    report_path = write_markdown_report(str(logfile), "summary", payload)

    expected = markdown_report_path(str(logfile), "summary")
    assert report_path == str(expected)
    content = expected.read_text(encoding="utf-8")
    assert "# LogScope summary report" in content
    assert "## malformed_count" in content
    assert "0" in content
    assert "## items" in content
