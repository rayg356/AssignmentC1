from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def to_json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def to_markdown(command: str, data: dict[str, Any]) -> str:
    lines: list[str] = [f"# LogScope {command} report", ""]
    for key, value in data.items():
        lines.append(f"## {key}")
        lines.append("")
        if isinstance(value, list):
            if not value:
                lines.append("- None")
            else:
                for item in value:
                    lines.append(f"- {item}")
        else:
            lines.append(str(value))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def markdown_report_path(logfile: str, command: str) -> Path:
    input_path = Path(logfile)
    return input_path.with_name(f"{input_path.stem}.{command}.report.md")


def write_markdown_report(logfile: str, command: str, data: dict[str, Any]) -> str:
    report_path = markdown_report_path(logfile, command)
    report_path.write_text(to_markdown(command, data), encoding="utf-8")
    return str(report_path)
