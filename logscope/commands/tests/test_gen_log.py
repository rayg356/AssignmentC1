from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from scripts.gen_log import generate_log, main


def test_generate_log_target_size_and_stats(tmp_path: Path) -> None:
    output = tmp_path / "synthetic.log"

    stats = generate_log(
        output=output,
        target_size_mb=1,
        seed=42,
        malformed_rate=0.01,
        start_time=datetime(2026, 10, 1, 9, 0, 0),
    )

    assert output.exists()
    assert stats["target_bytes"] == 1 * 1024 * 1024
    assert stats["size_bytes"] >= stats["target_bytes"]
    assert stats["size_bytes"] == output.stat().st_size
    assert stats["total_lines"] == stats["valid_lines"] + stats["malformed_lines"]
    assert stats["valid_lines"] > 0
    assert stats["malformed_lines"] > 0


def test_generate_log_reproducible_bytes(tmp_path: Path) -> None:
    out_a = tmp_path / "a.log"
    out_b = tmp_path / "b.log"

    generate_log(
        output=out_a,
        target_size_mb=1,
        seed=7,
        malformed_rate=0.02,
        start_time=datetime(2026, 10, 1, 9, 0, 0),
    )
    generate_log(
        output=out_b,
        target_size_mb=1,
        seed=7,
        malformed_rate=0.02,
        start_time=datetime(2026, 10, 1, 9, 0, 0),
    )

    assert out_a.read_bytes() == out_b.read_bytes()


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["gen_log.py", "--output", "x.log", "--size-mb", "0"], "size-mb must be > 0"),
        (
            ["gen_log.py", "--output", "x.log", "--malformed-rate", "1.5"],
            "malformed-rate must be between 0 and 1",
        ),
        (
            ["gen_log.py", "--output", "x.log", "--start-time", "bad-ts"],
            "invalid start-time, expected YYYY-MM-DD HH:MM:SS",
        ),
    ],
)
def test_main_validation_errors(monkeypatch: pytest.MonkeyPatch, argv: list[str], message: str) -> None:
    monkeypatch.setattr("sys.argv", argv)
    with pytest.raises(SystemExit, match=message):
        main()
