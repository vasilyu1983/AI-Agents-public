#!/usr/bin/env python3
"""
explain_collector.py — Stdlib-only PostgreSQL EXPLAIN JSON collector (estimated by default).

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
  # From a file (one statement per line; one optional final semicolon):
  python explain_collector.py --queries queries.txt

  # From stdin:
  echo "SELECT * FROM users WHERE id = 1" | python explain_collector.py

  # Estimated plan (default; the statement is not executed):
  python explain_collector.py --queries queries.txt --no-analyze

  # Execute a reviewed query on a disposable test database:
  python explain_collector.py --queries queries.txt --analyze

  # Write output to a file instead of stdout:
  python explain_collector.py --queries queries.txt --output plans.jsonl

  # Increase per-query timeout (default 30s):
  python explain_collector.py --queries queries.txt --timeout 60

FAILURE SEMANTICS
-----------------
- Each query runs as separate psql commands (BEGIN / SET LOCAL
  statement_timeout / EXPLAIN / ROLLBACK) with ON_ERROR_STOP, so the plan is
  printed on every psql version (a single multi-statement -c string made
  psql 14 print only the final ROLLBACK).
- --timeout is enforced server-side via statement_timeout, so a runaway
  EXPLAIN ANALYZE is cancelled on the server, not just abandoned by the client.
  If the client still hangs past timeout + grace, the script calls
  pg_cancel_backend() on the backend it tagged with a unique application_name.
- A record is "success": true only when a plan JSON was parsed. A missing or
  unparseable plan is a failure; the script exits non-zero if any query failed.

KNOWN LIMITATIONS
-----------------
- JIT details, when present, are retained in raw EXPLAIN JSON but are not
  surfaced separately. EXPLAIN fields are distinct from pg_stat_statements
  columns; interpret them using the installed version's documentation.
- Parameterised queries ($1, $2 ...) need concrete parameter values in this
  collector; --no-analyze does not bind parameters or create a generic plan.
- --analyze executes each query. ROLLBACK reverses transactional writes, but
  not sequence increments or external effects of functions. Review functions
  and triggers before executing; a replica is not a sandbox for side effects.
- Multi-statement inputs (queries separated by ; on the same line) are NOT
  supported. Each line must be a single, complete SQL statement. Internal
  semicolons, even inside literals/comments, are conservatively rejected.
"""

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone

# Extra seconds the client waits beyond statement_timeout before it gives up
# and cancels the server backend itself.
CLIENT_GRACE_SECONDS = 5


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
    """Trim whitespace; statement validation handles one optional terminator."""
    return raw.strip()


def _load_queries(path: str | None) -> list[str]:
    """Load queries from a file or stdin. One query per line."""
    if path:
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.readlines()
        except OSError as exc:
            sys.exit(f"ERROR: cannot read --queries file '{path}': {exc.strerror}. "
                     "Pass an existing file with one SQL statement per line.")
    else:
        lines = sys.stdin.readlines()

    queries = []
    for line in lines:
        stripped = _strip_query(line)
        # Skip blank lines and SQL-style single-line comments
        if stripped and not stripped.startswith("--"):
            queries.append(stripped)
    return queries


def _build_explain_commands(query: str, analyze: bool, timeout: int) -> list[str]:
    """Return the psql commands, each passed as its own -c argument.

    The transaction rolls back transactional writes, not arbitrary side
    effects (e.g. sequence increments). statement_timeout is local, so the
    server cancels the statement itself when the timeout is reached.
    """
    query = _strip_query(query).removesuffix(";").strip()
    if not query or ";" in query or "\n" in query or "\r" in query:
        raise ValueError("Expected one SQL statement on one line; internal semicolons are unsupported")
    options = "ANALYZE, BUFFERS, FORMAT JSON" if analyze else "FORMAT JSON"
    return [
        "BEGIN",
        f"SET LOCAL statement_timeout = '{int(timeout) * 1000}ms'",
        f"EXPLAIN ({options}) {query}",
        "ROLLBACK",
    ]


def _psql_base(database_url: str) -> list[str]:
    return [
        "psql",
        database_url,
        "-X",                     # do not read ~/.psqlrc
        "-q",                     # quiet: no BEGIN/SET/ROLLBACK command tags
        "-A",                     # unaligned output (no column padding)
        "-t",                     # tuples only (no headers or row counts)
        "-v", "ON_ERROR_STOP=1",  # non-zero exit on the first SQL error
    ]


def _cancel_backend(database_url: str, app_name: str) -> str:
    """Best-effort server-side cancel of the backend tagged with app_name."""
    sql = (
        "SELECT count(pg_cancel_backend(pid)) FROM pg_stat_activity "
        f"WHERE application_name = '{app_name}' AND pid <> pg_backend_pid()"
    )
    try:
        res = subprocess.run(
            _psql_base(database_url) + ["-c", sql],
            capture_output=True, text=True, timeout=10,
        )
        if res.returncode == 0:
            return f"cancelled {res.stdout.strip() or '0'} server backend(s)"
        return f"server cancel failed: {res.stderr.strip()[:200]}"
    except (subprocess.TimeoutExpired, OSError) as exc:
        return f"server cancel failed: {exc}"


def _run_psql(database_url: str, commands: list[str], timeout: int) -> tuple[str, str, int]:
    """
    Execute commands via psql and return (stdout, stderr, returncode).
    Each command is a separate -c argument so psql prints every result.
    """
    app_name = f"explain_collector_{uuid.uuid4().hex[:12]}"
    cmd = _psql_base(database_url)
    for c in commands:
        cmd += ["-c", c]
    env = dict(os.environ, PGAPPNAME=app_name)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + CLIENT_GRACE_SECONDS,
            env=env,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        note = _cancel_backend(database_url, app_name)
        return "", f"psql client timed out after {timeout + CLIENT_GRACE_SECONDS}s; {note}", 1
    except FileNotFoundError:
        sys.exit(
            "ERROR: psql not found on PATH. Install the PostgreSQL client:\n"
            "  macOS:  brew install libpq\n"
            "  Ubuntu: apt-get install postgresql-client\n"
        )


def _is_plan(value) -> bool:
    """Recognize the EXPLAIN JSON envelope, rather than arbitrary JSON."""
    return (
        isinstance(value, list) and len(value) == 1
        and isinstance(value[0], dict)
        and isinstance(value[0].get("Plan"), dict)
        and isinstance(value[0]["Plan"].get("Node Type"), str)
        and bool(value[0]["Plan"]["Node Type"].strip())
    )


def _parse_plan_json(raw_stdout: str) -> list | None:
    """
    psql in tuples-only mode outputs the JSON value directly.
    pg EXPLAIN FORMAT JSON returns a JSON array with one element.
    """
    text = raw_stdout.strip()
    if not text:
        return None
    try:
        value = json.loads(text)
        return value if _is_plan(value) else None
    except json.JSONDecodeError:
        pass
    # Tolerate stray non-JSON lines (e.g. command tags) around a multi-line
    # JSON document: decode from the first '[' that parses.
    decoder = json.JSONDecoder()
    start = text.find("[")
    while start != -1:
        try:
            value, _ = decoder.raw_decode(text[start:])
            if _is_plan(value):
                return value
            start = text.find("[", start + 1)
        except json.JSONDecodeError:
            start = text.find("[", start + 1)
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
) -> int:
    """Run EXPLAIN for each query, write JSONL records, return failure count."""
    total = len(queries)
    failures = 0
    for idx, query in enumerate(queries, start=1):
        try:
            commands = _build_explain_commands(query, analyze=analyze, timeout=timeout)
        except ValueError as exc:
            stdout, stderr, returncode = "", str(exc), 1
        else:
            stdout, stderr, returncode = _run_psql(database_url, commands, timeout)

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
                record["success"] = False
                record["error"] = "psql exited 0 but no EXPLAIN JSON plan was found in stdout"
                record["raw_stdout"] = stdout.strip()
                _log(f"[{idx}/{total}] ERROR — could not parse plan JSON", file=sys.stderr)
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

        if not record["success"]:
            failures += 1
        output_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        output_fh.flush()
    return failures


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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--analyze", action="store_true", default=False,
        help="Execute the reviewed statement and collect actual timings. "
             "Rollback cannot undo sequence or external function effects.",
    )
    mode.add_argument(
        "--no-analyze",
        action="store_true",
        default=False,
        help="Use estimated EXPLAIN (the default). The statement is not executed, "
             "but planning still acquires locks and may evaluate immutable functions.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        metavar="SECONDS",
        help="Per-query timeout in seconds, enforced server-side via "
             "statement_timeout (default: 30).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.timeout <= 0:
        sys.exit("ERROR: --timeout must be a positive number of seconds.")

    database_url = _get_database_url()
    queries = _load_queries(args.queries)

    if not queries:
        sys.exit("ERROR: No queries found. Provide a non-empty --queries file or pipe queries via stdin.")

    analyze = args.analyze

    _log(
        f"Starting: {len(queries)} quer{'y' if len(queries) == 1 else 'ies'}, "
        f"analyze={'yes (--analyze)' if analyze else 'no (estimated)'}, "
        f"timeout={args.timeout}s",
        file=sys.stderr,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            failures = collect_plans(queries, database_url, analyze, args.timeout, fh)
        _log(f"Done. Output written to {args.output}", file=sys.stderr)
    else:
        failures = collect_plans(queries, database_url, analyze, args.timeout, sys.stdout)
        _log("Done.", file=sys.stderr)

    if failures:
        _log(f"{failures}/{len(queries)} quer{'y' if failures == 1 else 'ies'} failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
