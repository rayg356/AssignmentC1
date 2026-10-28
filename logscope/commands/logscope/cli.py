from __future__ import annotations

import argparse
import sys
from datetime import datetime

from logscope.commands.grep_cmd import grep_to_payload, parse_since, render_grep_text, run_grep
from logscope.commands.summary import render_summary_text, run_summary, summary_to_payload
from logscope.commands.timeline import render_timeline_text, run_timeline, timeline_to_payload
from logscope.renderers import to_json, write_markdown_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="logscope")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary_parser = subparsers.add_parser("summary", help="Summarize a log file")
    summary_parser.add_argument("logfile")
    summary_parser.add_argument("--format", choices=["text", "json", "md"], default="text")

    timeline_parser = subparsers.add_parser("timeline", help="Show ERROR timeline")
    timeline_parser.add_argument("logfile")
    timeline_parser.add_argument("--bucket", default="15m")
    timeline_parser.add_argument("--format", choices=["text", "json", "md"], default="text")

    grep_parser = subparsers.add_parser("grep", help="Filter log lines")
    grep_parser.add_argument("logfile")
    grep_parser.add_argument("--level", required=True, choices=["INFO", "WARN", "ERROR"])
    grep_parser.add_argument("--since")
    grep_parser.add_argument("--format", choices=["text", "json", "md"], default="text")

    return parser


def _open_lines(logfile: str):
    try:
        return open(logfile, "r", encoding="utf-8")
    except OSError as exc:
        print(f"Error: cannot read file '{logfile}': {exc}", file=sys.stderr)
        return None


def _emit_output(command: str, logfile: str, fmt: str, payload: dict[str, object], text: str) -> int:
    if fmt == "text":
        print(text)
        return 0
    if fmt == "json":
        print(to_json(payload))
        return 0
    if fmt == "md":
        path = write_markdown_report(logfile, command, payload)
        print(path)
        return 0
    print(f"Error: unsupported format '{fmt}'", file=sys.stderr)
    return 2


def run_from_args(args: argparse.Namespace) -> int:
    if args.command == "summary":
        handle = _open_lines(args.logfile)
        if handle is None:
            return 1
        with handle:
            result = run_summary(handle)
        return _emit_output(
            command="summary",
            logfile=args.logfile,
            fmt=args.format,
            payload=summary_to_payload(result),
            text=render_summary_text(result),
        )

    if args.command == "timeline":
        handle = _open_lines(args.logfile)
        if handle is None:
            return 1
        try:
            with handle:
                result = run_timeline(handle, bucket=args.bucket)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        return _emit_output(
            command="timeline",
            logfile=args.logfile,
            fmt=args.format,
            payload=timeline_to_payload(result),
            text=render_timeline_text(result),
        )

    if args.command == "grep":
        handle = _open_lines(args.logfile)
        if handle is None:
            return 1

        since_dt: datetime | None = None
        if args.since is not None:
            try:
                since_dt = parse_since(args.since)
            except ValueError:
                print(
                    "Error: invalid --since timestamp, expected YYYY-MM-DD HH:MM",
                    file=sys.stderr,
                )
                return 2

        try:
            with handle:
                result = run_grep(handle, level=args.level, since=since_dt)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2

        return _emit_output(
            command="grep",
            logfile=args.logfile,
            fmt=args.format,
            payload=grep_to_payload(result),
            text=render_grep_text(result),
        )

    print("Error: unknown command", file=sys.stderr)
    return 2
