#!/usr/bin/env python3
"""
explain_collector.py — Stdlib-only EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) collector.

Connects to PostgreSQL via psql (subprocess) using DATABASE_URL, runs each
query through EXPLAIN, and writes results as JSONL to stdout or a file.

REQUIREMENTS
------------
- psql must be on PATH (PostgreSQL client, not the server)
- DATABASE_URL env var must be set:
    postgresql://user:password@host:5432/dbname
  or any libpq-compatible connection string.

USAGE
-----
  # From a file of queries (one per line, terminated by semicolons stripped):
  python explain_collector.py --queries queries.txt

  # From stdin:
  echo "SELECT * FROM users WHERE id = 1" | python explain_collector.py

  # Production-safe mode (EXPLAIN without ANALYZE — no query execution):
  python explain_collector.py --queries queries.txt --no-analyze

  # Write output to a file instead of stdout:
  python explain_collector.py --queries queries.txt --output plans.jsonl

  # Increase per-query timeout (default 30s):
  python explain_collector.py --queries queries.txt --timeout 60

KNOWN LIMITATIONS
-----------------
- JIT timing (jit_*) columns available in PG16+ are captured in the raw JSON
  but NOT parsed or surfaced separately. Treat jit_* fields as opaque blobs for
  now; a future iteration can extract them.
- Parameterised queries ($1, $2 ...) from pg_stat_statements cannot be run
  with ANALYZE — use --no-analyze or substitute real parameter values first.
- ANALYZE mode runs each query against the live database. Use a replica or
  --no-analyze for production-sensitive workloads.
- Multi-statement inputs (queries separated by ; on the same line) are NOT
  supported. Each line must be a single, complete SQL statement.
"""

import argparse
import json
import os
import subprocess
import sys
import textwrap
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        sys.exit(
            "ERROR: DATABASE_URL environment variable is not set.\n"
            "  Example: export DATABASE_URL='postgresql://user:pass@localhost:5432/mydb'"
        )
    return url


def _strip_query(raw: str) -> str:
    """Normalise a single query: strip whitespace and trailing semicolons."""
    return raw.strip().rstrip(";").strip()


def _load_queries(path: str | None) -> list[str]:
    """Load queries from a file or stdin. One query per line."""
    if path:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
    else:
        lines = sys.stdin.readlines()

    queries = []
    for line in lines:
        stripped = _strip_query(line)
        # Skip blank lines and SQL-style single-line comments
        if stripped and not stripped.startswith("--"):
            queries.append(stripped)
    return queries


def _build_explain_sql(query: str, analyze: bool) -> str:
    """Wrap a query in EXPLAIN with JSON output."""
    options = "ANALYZE, BUFFERS, FORMAT JSON" if analyze else "BUFFERS, FORMAT JSON"
    # Wrap in a transaction so ANALYZE changes are always rolled back, preventing
    # accidental side-effects from data-modifying statements.
    return textwrap.dedent(f"""\
        BEGIN;
        EXPLAIN ({options})
        {query};
        ROLLBACK;
    """)


def _run_psql(database_url: str, sql: str, timeout: int) -> tuple[str, str, int]:
    """
    Execute sql via psql and return (stdout, stderr, returncode).
    Uses -X to skip .psqlrc, -A for unaligned output, -t for tuples-only.
    """
    cmd = [
        "psql",
        database_url,
        "-X",      # do not read ~/.psqlrc
        "-A",      # unaligned output (no column padding)
        "-t",      # tuples only (no headers or row counts)
        "-c", sql,
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"psql timed out after {timeout}s", 1
    except FileNotFoundError:
        sys.exit(
            "ERROR: psql not found on PATH. Install the PostgreSQL client:\n"
            "  macOS:  brew install libpq\n"
            "  Ubuntu: apt-get install postgresql-client\n"
        )


def _parse_plan_json(raw_stdout: str) -> dict | list | None:
    """
    psql in tuples-only mode outputs the JSON value directly.
    pg EXPLAIN FORMAT JSON returns a JSON array with one element.
    """
    text = raw_stdout.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Might be multi-line output from BEGIN/ROLLBACK — extract JSON array
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("["):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    pass
        return None


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def collect_plans(
    queries: list[str],
    database_url: str,
    analyze: bool,
    timeout: int,
    output_fh,
) -> None:
    """Run EXPLAIN for each query and write JSONL records."""
    total = len(queries)
    for idx, query in enumerate(queries, start=1):
        sql = _build_explain_sql(query, analyze=analyze)
        stdout, stderr, returncode = _run_psql(database_url, sql, timeout)

        record: dict = {
            "index": idx,
            "total": total,
            "query": query,
            "analyze": analyze,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "success": returncode == 0,
        }

        if returncode != 0:
            record["error"] = stderr.strip()
            record["plan"] = None
            _log(f"[{idx}/{total}] ERROR — {stderr.strip()[:120]}", file=sys.stderr)
        else:
            plan = _parse_plan_json(stdout)
            record["plan"] = plan
            if plan is None:
                record["raw_stdout"] = stdout.strip()
                _log(f"[{idx}/{total}] WARNING — could not parse plan JSON", file=sys.stderr)
            else:
                # Surface top-level cost for quick scanning of the JSONL
                try:
                    top_node = plan[0]["Plan"]
                    record["total_cost"] = top_node.get("Total Cost")
                    record["actual_total_time_ms"] = top_node.get("Actual Total Time")
                    record["rows"] = top_node.get("Actual Rows")
                except (KeyError, IndexError, TypeError):
                    pass
                _log(f"[{idx}/{total}] OK — {query[:80]}", file=sys.stderr)

        output_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        output_fh.flush()


def _log(msg: str, file=sys.stderr) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=file)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--queries", "-q",
        metavar="FILE",
        default=None,
        help="Path to a file containing SQL queries, one per line. "
             "Reads from stdin if omitted.",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        default=None,
        help="Output JSONL file path. Writes to stdout if omitted.",
    )
    parser.add_argument(
        "--no-analyze",
        action="store_true",
        default=False,
        help="Use EXPLAIN without ANALYZE. Safe for production — queries are "
             "NOT executed. Plans are estimated only.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        metavar="SECONDS",
        help="Per-query psql timeout in seconds (default: 30).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    database_url = _get_database_url()
    queries = _load_queries(args.queries)

    if not queries:
        sys.exit("ERROR: No queries found. Provide a non-empty --queries file or pipe queries via stdin.")

    analyze = not args.no_analyze

    _log(
        f"Starting: {len(queries)} quer{'y' if len(queries) == 1 else 'ies'}, "
        f"analyze={'yes' if analyze else 'no (--no-analyze)'}, "
        f"timeout={args.timeout}s",
        file=sys.stderr,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            collect_plans(queries, database_url, analyze, args.timeout, fh)
        _log(f"Done. Output written to {args.output}", file=sys.stderr)
    else:
        collect_plans(queries, database_url, analyze, args.timeout, sys.stdout)
        _log("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
