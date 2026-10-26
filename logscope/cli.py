from __future__ import annotations

import argparse
import sys
from datetime import datetime

from logscope.commands.summary import SummaryResult, run_summary


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

    return parser


def run_from_args(args: argparse.Namespace) -> int:
    if args.command == "summary":
        try:
            with open(args.logfile, "r", encoding="utf-8") as handle:
                result = run_summary(handle)
        except OSError as exc:
            print(f"Error: cannot read file '{args.logfile}': {exc}", file=sys.stderr)
            return 1

        _print_summary(result)
        return 0

    print("Error: unknown command", file=sys.stderr)
    return 2
