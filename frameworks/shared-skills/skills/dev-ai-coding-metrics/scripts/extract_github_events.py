"""
extract_github_events.py — GitHub telemetry extractor for AI coding metrics.

Pulls pull-request or commit data from the GitHub REST API using only the
Python standard library (urllib + json). Outputs CSV to stdout or a file.

Usage:
  python extract_github_events.py pulls  --repo owner/name --since 2025-01-01
  python extract_github_events.py commits --repo owner/name --since 2025-01-01 --output out.csv

Requirements:
  GITHUB_TOKEN environment variable must be set (classic PAT or fine-grained
  token with repo:read scope). Works with public repos without a token but
  rate limits are lower (60 req/h vs 5000 req/h).

Rate-limit policy:
  Reads X-RateLimit-Remaining on every response. When remaining < 20, sleeps
  until X-RateLimit-Reset (UNIX timestamp returned by the API).

Pagination:
  Follows RFC 5988 Link headers (rel="next") automatically.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Generator, Iterator


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

GITHUB_API = "https://api.github.com"
_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def _headers() -> dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if _TOKEN:
        h["Authorization"] = f"Bearer {_TOKEN}"
    return h


def _check_rate_limit(response_headers: Any) -> None:
    """Sleep until rate-limit resets if remaining budget is low."""
    remaining = response_headers.get("X-RateLimit-Remaining")
    reset_at = response_headers.get("X-RateLimit-Reset")
    if remaining is not None and int(remaining) < 20:
        if reset_at is not None:
            reset_ts = int(reset_at)
            now_ts = int(time.time())
            wait = max(reset_ts - now_ts + 2, 1)
            print(
                f"[rate-limit] Remaining={remaining}; sleeping {wait}s until reset.",
                file=sys.stderr,
            )
            time.sleep(wait)


def _get(url: str) -> tuple[Any, Any]:
    """HTTP GET; returns (parsed_json, http.client.HTTPResponse headers)."""
    req = urllib.request.Request(url, headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            _check_rate_limit(resp.headers)
            return json.loads(resp.read()), resp.headers
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body}") from exc


def _paginate(url: str) -> Generator[Any, None, None]:
    """Yield all pages from a paginated GitHub endpoint."""
    while url:
        data, headers = _get(url)
        yield data
        link_header = headers.get("Link", "")
        url = _parse_next_link(link_header)


def _parse_next_link(link_header: str) -> str | None:
    """Parse RFC 5988 Link header, return URL for rel=next or None."""
    if not link_header:
        return None
    for part in link_header.split(","):
        parts = [p.strip() for p in part.split(";")]
        if len(parts) == 2 and parts[1] == 'rel="next"':
            return parts[0].strip("<>")
    return None


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def _iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _hours_between(a: datetime | None, b: datetime | None) -> str:
    if a is None or b is None:
        return ""
    delta = (b - a).total_seconds() / 3600
    return f"{delta:.2f}"


def _open_output(path: str | None) -> io.TextIOWrapper:
    if path:
        return open(path, "w", newline="", encoding="utf-8")
    return sys.stdout


# ---------------------------------------------------------------------------
# Subcommand: pulls
# ---------------------------------------------------------------------------

PULLS_FIELDS = [
    "pr_number",
    "author",
    "opened_at",
    "merged_at",
    "additions",
    "deletions",
    "changed_files",
    "review_count",
    "time_to_first_review_h",
    "time_to_merge_h",
]


def _fetch_pr_details(repo: str, pr_number: int) -> dict[str, Any]:
    url = f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}"
    data, _ = _get(url)
    return data


def _fetch_pr_reviews(repo: str, pr_number: int) -> list[dict[str, Any]]:
    url = f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/reviews?per_page=100"
    reviews: list[dict] = []
    for page in _paginate(url):
        reviews.extend(page)
    return reviews


def cmd_pulls(args: argparse.Namespace) -> None:
    repo = args.repo
    since = args.since  # ISO date string, e.g. "2025-01-01"
    output_path = args.output

    url = (
        f"{GITHUB_API}/repos/{repo}/pulls"
        f"?state=closed&sort=created&direction=desc&per_page=100"
    )

    out = _open_output(output_path)
    try:
        writer = csv.DictWriter(out, fieldnames=PULLS_FIELDS, lineterminator="\n")
        writer.writeheader()

        for page in _paginate(url):
            stop = False
            for pr in page:
                opened_at = _iso(pr.get("created_at"))
                if opened_at and opened_at.isoformat() < since:
                    stop = True
                    break

                # Merged PRs only
                if not pr.get("merged_at"):
                    continue

                pr_number = pr["number"]
                author = (pr.get("user") or {}).get("login", "")
                merged_at = _iso(pr.get("merged_at"))

                # Detail endpoint for additions/deletions/changed_files
                detail = _fetch_pr_details(repo, pr_number)
                additions = detail.get("additions", "")
                deletions = detail.get("deletions", "")
                changed_files = detail.get("changed_files", "")

                # Reviews
                reviews = _fetch_pr_reviews(repo, pr_number)
                review_count = len(reviews)
                first_review_at = None
                if reviews:
                    first_review_at = min(
                        (_iso(r.get("submitted_at")) for r in reviews if r.get("submitted_at")),
                        default=None,
                    )

                writer.writerow(
                    {
                        "pr_number": pr_number,
                        "author": author,
                        "opened_at": pr.get("created_at", ""),
                        "merged_at": pr.get("merged_at", ""),
                        "additions": additions,
                        "deletions": deletions,
                        "changed_files": changed_files,
                        "review_count": review_count,
                        "time_to_first_review_h": _hours_between(opened_at, first_review_at),
                        "time_to_merge_h": _hours_between(opened_at, merged_at),
                    }
                )

            if stop:
                break

    finally:
        if output_path:
            out.close()


# ---------------------------------------------------------------------------
# Subcommand: commits
# ---------------------------------------------------------------------------

COMMITS_FIELDS = [
    "sha",
    "author",
    "date",
    "additions",
    "deletions",
]


def _fetch_commit_detail(repo: str, sha: str) -> dict[str, Any]:
    url = f"{GITHUB_API}/repos/{repo}/commits/{sha}"
    data, _ = _get(url)
    return data


def cmd_commits(args: argparse.Namespace) -> None:
    repo = args.repo
    since = args.since
    output_path = args.output

    url = (
        f"{GITHUB_API}/repos/{repo}/commits"
        f"?since={since}T00:00:00Z&per_page=100"
    )

    out = _open_output(output_path)
    try:
        writer = csv.DictWriter(out, fieldnames=COMMITS_FIELDS, lineterminator="\n")
        writer.writeheader()

        for page in _paginate(url):
            for commit in page:
                sha = commit["sha"]
                author_login = (
                    (commit.get("author") or {}).get("login")
                    or (commit.get("commit", {}).get("author") or {}).get("name", "")
                )
                date = (commit.get("commit", {}).get("author") or {}).get("date", "")

                detail = _fetch_commit_detail(repo, sha)
                stats = detail.get("stats", {})
                additions = stats.get("additions", "")
                deletions = stats.get("deletions", "")

                writer.writerow(
                    {
                        "sha": sha,
                        "author": author_login,
                        "date": date,
                        "additions": additions,
                        "deletions": deletions,
                    }
                )
    finally:
        if output_path:
            out.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="extract_github_events",
        description=(
            "Extract GitHub PR or commit telemetry to CSV. "
            "Set GITHUB_TOKEN env var for authenticated requests (5000 req/h vs 60)."
        ),
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    # pulls subcommand
    pulls_p = sub.add_parser(
        "pulls",
        help="Export merged PR metrics: number, author, timings, review count.",
    )
    pulls_p.add_argument("--repo", required=True, metavar="OWNER/NAME", help="e.g. torvalds/linux")
    pulls_p.add_argument(
        "--since",
        required=True,
        metavar="YYYY-MM-DD",
        help="Include PRs opened on or after this date.",
    )
    pulls_p.add_argument("--output", metavar="FILE", help="Write CSV here (default: stdout).")

    # commits subcommand
    commits_p = sub.add_parser(
        "commits",
        help="Export commit metrics: sha, author, date, additions, deletions.",
    )
    commits_p.add_argument("--repo", required=True, metavar="OWNER/NAME")
    commits_p.add_argument("--since", required=True, metavar="YYYY-MM-DD")
    commits_p.add_argument("--output", metavar="FILE", help="Write CSV here (default: stdout).")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.subcommand == "pulls":
        cmd_pulls(args)
    elif args.subcommand == "commits":
        cmd_commits(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
