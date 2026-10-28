from __future__ import annotations

import sys

from logscope.cli import build_parser, run_from_args


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return run_from_args(args)


if __name__ == "__main__":
    sys.exit(main())
