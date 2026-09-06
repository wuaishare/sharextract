from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .router import extract


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sharextract",
        description="Extract normalized content from a public share URL.",
    )
    parser.add_argument("url", help="Public http(s) URL to extract")
    parser.add_argument(
        "--strategy",
        choices=("auto", "native", "media", "web"),
        default="auto",
        help="Extraction strategy (default: auto)",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown", "text"),
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument("--output", "-o", help="Write output to a file instead of stdout")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--max-bytes", type=int, default=8 * 1024 * 1024)
    parser.add_argument("--compact", action="store_true", help="Compact JSON output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = extract(
            args.url,
            strategy=args.strategy,
            timeout=args.timeout,
            max_bytes=args.max_bytes,
        )
        rendered = _render(result, args.format, compact=args.compact)
    except Exception as exc:
        print(f"sharextract: {exc}", file=sys.stderr)
        return 2

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0


def _render(result, fmt: str, *, compact: bool) -> str:
    if fmt == "markdown":
        return result.markdown or result.text
    if fmt == "text":
        return result.text or result.markdown
    return json.dumps(
        result.to_dict(),
        ensure_ascii=False,
        indent=None if compact else 2,
        separators=(",", ":") if compact else None,
    )


if __name__ == "__main__":
    raise SystemExit(main())
