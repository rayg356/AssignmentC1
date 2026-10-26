from __future__ import annotations

import argparse
import sys
from datetime import datetime

from logscope.commands.summary import SummaryResult, run_summary
from logscope.commands.timeline import render_timeline_text, run_timeline


def _format_timestamp(value: datetime | None) -> str:
    if value is None:
        return "N/A"
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _print_summary(result: SummaryResult) -> None:
    print(f"INFO: {result.info_count}")
    print(f"WARN: {result.warn_count}")
    print(f"ERROR: {result.error_count}")
    print(f"First timestamp: {_format_timestamp(result.first_timestamp)}")
    print(f"Last timestamp: {_format_timestamp(result.last_timestamp)}")
    print(f"Malformed lines: {result.malformed_count}")
    print("Top 5 error messages:")
    if not result.top_errors:
        print("- None")
        return
    for message, count in result.top_errors:
        print(f"- {message}: {count}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="logscope")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary_parser = subparsers.add_parser("summary", help="Summarize a log file")
    summary_parser.add_argument("logfile")

    timeline_parser = subparsers.add_parser("timeline", help="Show ERROR timeline")
    timeline_parser.add_argument("logfile")
    timeline_parser.add_argument("--bucket", default="15m")

    return parser


def _open_lines(logfile: str):
    try:
        return open(logfile, "r", encoding="utf-8")
    except OSError as exc:
        print(f"Error: cannot read file '{logfile}': {exc}", file=sys.stderr)
        return None


def run_from_args(args: argparse.Namespace) -> int:
    if args.command == "summary":
        handle = _open_lines(args.logfile)
        if handle is None:
            return 1
        with handle:
            result = run_summary(handle)
        _print_summary(result)
        return 0

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
        print(render_timeline_text(result))
        return 0

    print("Error: unknown command", file=sys.stderr)
    return 2
