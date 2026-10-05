#!/usr/bin/env python3
"""
log_error_summary.py — Fast first-pass log triage.

Groups error/exception/panic lines by normalised signature and prints the
top-N groups by occurrence count with a sample line from each group.

Usage:
    python3 log_error_summary.py path/to/logfile [--top N]
    cat logfile | python3 log_error_summary.py - [--top N]

Exit codes: 0 = input scanned (with or without matches), 2 = unusable input
(missing, unreadable, directory, empty, or binary). An empty or binary input
fails loudly instead of reporting "no errors", because a wrong path or a
rotated-away log must not read as a clean log.

Stdlib only. No third-party dependencies.
"""

import argparse
import re
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# Patterns that flag a line as worth collecting
# ---------------------------------------------------------------------------
_INTEREST_RE = re.compile(
    r"\b(?:error|exception|panic|fatal|critical|traceback|failed|failure|warning)\b"
    r"|\b(?:err|warn):",
    re.IGNORECASE,
)

class InputError(Exception):
    """Raised when the input cannot be treated as a text log."""

# ---------------------------------------------------------------------------
# Normalisation substitutions applied in order before grouping.
# Each tuple is (compiled_pattern, replacement).
# ---------------------------------------------------------------------------
_NORMALISE: list[tuple[re.Pattern, str]] = [
    # ISO-8601 / common timestamps
    (re.compile(
        r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?"
    ), "<TIMESTAMP>"),
    # Epoch/unix timestamps (10-13 digit numbers)
    (re.compile(r"\b\d{10,13}\b"), "<EPOCH>"),
    # UUIDs
    (re.compile(
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
    ), "<UUID>"),
    # Hex addresses / pointers
    (re.compile(r"\b0x[0-9a-fA-F]{4,}\b"), "<ADDR>"),
    # IP addresses (v4)
    (re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d{1,5})?\b"), "<IP>"),
    # Long decimal numbers (IDs, ports, line numbers in stack traces)
    (re.compile(r"\b\d{4,}\b"), "<NUM>"),
    # File paths (Unix-style)
    (re.compile(r"(?:/[\w.\-]+){3,}"), "<PATH>"),
    # Quoted strings
    (re.compile(r'"[^"]{0,120}"'), "<STR>"),
    (re.compile(r"'[^']{0,120}'"), "<STR>"),
    # Request IDs / trace IDs (alphanumeric tokens 16+ chars that look like IDs)
    (re.compile(r"\b[a-zA-Z0-9]{16,64}\b"), "<ID>"),
    # Collapse runs of whitespace
    (re.compile(r"\s+"), " "),
]


def normalise(line: str) -> str:
    """Return a normalised signature for grouping similar log lines."""
    sig = line
    for pattern, replacement in _NORMALISE:
        sig = pattern.sub(replacement, sig)
    return sig.strip()


def collect(source, top_n: int) -> None:
    """Read lines from *source*, group by signature, print summary."""
    groups: dict[str, list[str]] = defaultdict(list)
    scanned = 0

    for raw_line in source:
        scanned += 1
        line = raw_line.rstrip("\n")
        if "\x00" in line:
            raise InputError("input looks binary (NUL bytes), not a text log")
        if any("\ud800" <= char <= "\udfff" for char in line):
            raise InputError("input contains undecodable UTF-8 bytes")
        if not _INTEREST_RE.search(line):
            continue
        sig = normalise(line)
        groups[sig].append(line)

    if scanned == 0:
        raise InputError("input is empty (0 lines); check the path or log rotation")

    if not groups:
        print(f"No error/exception/panic lines found in {scanned} scanned lines.")
        return

    # Sort by descending count, then by signature for determinism
    ranked = sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    top = ranked[:top_n]
    total_groups = len(ranked)
    total_lines = sum(len(v) for v in groups.values())

    print(f"{'='*72}")
    print(f"Log Error Summary  —  {total_lines} matching lines in {total_groups} groups"
          f" ({scanned} lines scanned)")
    print(f"Showing top {len(top)} of {total_groups} groups")
    print(f"{'='*72}\n")

    for rank, (sig, lines) in enumerate(top, start=1):
        count = len(lines)
        sample = lines[0]
        print(f"[#{rank}]  count={count}")
        print(f"  signature : {sig[:120]}")
        print(f"  sample    : {sample[:200]}")
        if count > 1:
            # Show a second distinct sample if available
            for other in lines[1:]:
                if other != lines[0]:
                    print(f"  sample2   : {other[:200]}")
                    break
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarise error/exception/panic lines from a log file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 log_error_summary.py app.log\n"
            "  python3 log_error_summary.py app.log --top 5\n"
            "  cat app.log | python3 log_error_summary.py -\n"
        ),
    )
    parser.add_argument(
        "logfile",
        help="Path to log file, or '-' to read from stdin.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        metavar="N",
        help="Number of top groups to show (default: 10).",
    )
    args = parser.parse_args()

    if args.top < 1:
        parser.error("--top must be >= 1")

    try:
        if args.logfile == "-":
            collect(sys.stdin, args.top)
        else:
            with open(args.logfile, encoding="utf-8") as fh:
                collect(fh, args.top)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print(f"error: file not found: {args.logfile}", file=sys.stderr)
        sys.exit(2)
    except IsADirectoryError:
        print(f"error: is a directory, not a log file: {args.logfile}", file=sys.stderr)
        sys.exit(2)
    except UnicodeDecodeError as exc:
        print(f"error: cannot read {args.logfile} as UTF-8 text: {exc}", file=sys.stderr)
        sys.exit(2)
    except OSError as exc:
        print(f"error: cannot read {args.logfile}: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
