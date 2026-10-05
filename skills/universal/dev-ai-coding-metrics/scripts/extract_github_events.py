"""
extract_github_events.py — GitHub telemetry extractor for AI coding metrics.

Pulls pull-request or commit data from the GitHub REST API using only the
Python standard library (urllib + json). Outputs CSV to stdout or a file.

Usage:
  python extract_github_events.py pulls  --repo owner/name --since 2025-01-01
  python extract_github_events.py commits --repo owner/name --since 2025-01-01 --output out.csv

Authentication:
  Public data can be read without a token. For private repositories, use an
  authorized GITHUB_TOKEN with endpoint-specific read permissions: Pull requests
  for PRs/reviews and Contents for commits. Check GitHub's current endpoint docs.
  Quotas vary by authentication; read response headers, not a fixed quota table.

Rate-limit policy:
  Stops on exhausted primary budget, reporting the reset time for a later retry.
  Never sleeps until an unbounded server-supplied timestamp.

Pagination:
  Follows RFC 5988 Link headers (rel="next") automatically.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import os
import sys
import urllib.error
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Generator, Iterator


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

GITHUB_API = "https://api.github.com"
_TOKEN = os.environ.get("GITHUB_TOKEN", "")
_LAST_RESPONSE_HEADERS = {}


def _headers() -> dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if _TOKEN:
        h["Authorization"] = f"Bearer {_TOKEN}"
    return h


def _check_rate_limit(response_headers: Any) -> None:
    remaining = response_headers.get("X-RateLimit-Remaining")
    if remaining is not None and int(remaining) == 0:
        raise RuntimeError("GitHub primary rate limit exhausted; retry after reset "
                           + str(response_headers.get("X-RateLimit-Reset", "(not provided)")))


def _validate_url(url: str) -> None:
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != "https" or parsed.netloc != "api.github.com"
            or parsed.username or parsed.password):
        raise RuntimeError("Refusing a request outside https://api.github.com")


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _get(url: str) -> tuple[Any, Any]:
    """HTTP GET; returns (parsed_json, http.client.HTTPResponse headers)."""
    global _LAST_RESPONSE_HEADERS
    _validate_url(url)
    _check_rate_limit(_LAST_RESPONSE_HEADERS)
    req = urllib.request.Request(url, headers=_headers())
    try:
        with urllib.request.build_opener(SafeRedirect()).open(req, timeout=30) as resp:
            _LAST_RESPONSE_HEADERS = resp.headers
            return json.loads(resp.read()), resp.headers
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GitHub HTTP {exc.code}; export incomplete") from exc


def _paginate(url: str) -> Generator[Any, None, None]:
    """Yield all pages from a paginated GitHub endpoint."""
    visited = set()
    while url:
        _validate_url(url)
        if url in visited:
            raise RuntimeError("Repeated pagination link; export incomplete")
        visited.add(url)
        data, headers = _get(url)
        if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
            raise RuntimeError("Expected a list of GitHub records; export incomplete")
        yield data
        link_header = headers.get("Link", "")
        url = _parse_next_link(link_header)


def _parse_next_link(link_header: str) -> str | None:
    """Parse RFC 5988 Link header, return URL for rel=next or None."""
    if not link_header:
        return None
    for part in link_header.split(","):
        parts = [p.strip() for p in part.split(";")]
        if 'rel="next"' in parts[1:]:
            candidate = parts[0].strip("<>")
            _validate_url(candidate)
            return candidate
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
    "state",
    "outcome",
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
    since = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc)
    output_path = args.output

    url = (
        f"{GITHUB_API}/repos/{repo}/pulls"
        f"?state=all&sort=created&direction=desc&per_page=100"
    )

    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=PULLS_FIELDS, lineterminator="\n")
    writer.writeheader()

    for page in _paginate(url):
        stop = False
        for pr in page:
            opened_at = _iso(pr.get("created_at"))
            if opened_at and opened_at < since:
                stop = True
                break

            if opened_at is None:
                raise RuntimeError("Missing PR creation timestamp; export incomplete")

            if pr.get("state") not in {"open", "closed"}:
                raise RuntimeError("Missing or invalid PR state; export incomplete")
            if pr.get("merged_at") and pr["state"] != "closed":
                raise RuntimeError("Inconsistent PR merge state; export incomplete")
            pr_number = pr["number"]
            author = (pr.get("user") or {}).get("login", "")
            merged_at = _iso(pr.get("merged_at"))

            # Detail endpoint for additions/deletions/changed_files
            detail = _fetch_pr_details(repo, pr_number)
            if not isinstance(detail, dict):
                raise RuntimeError("Expected PR details object; export incomplete")
            for key in ("additions", "deletions", "changed_files"):
                value = detail.get(key)
                if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                    raise RuntimeError(f"Missing or invalid PR {key}; export incomplete")
            additions = detail["additions"]
            deletions = detail["deletions"]
            changed_files = detail["changed_files"]

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
                    "state": pr.get("state", ""),
                    "outcome": "merged" if pr.get("merged_at") else ("still_open" if pr.get("state") == "open" else "closed_unmerged"),
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

    result = out.getvalue()
    if output_path:
        with _open_output(output_path) as destination:
            destination.write(result)
    else:
        sys.stdout.write(result)


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

    out = io.StringIO()
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
    result = out.getvalue()
    if output_path:
        with _open_output(output_path) as destination:
            destination.write(result)
    else:
        sys.stdout.write(result)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="extract_github_events",
        description=(
            "Extract GitHub PR or commit telemetry to CSV. "
            "Set GITHUB_TOKEN for authorized private-repository access."
        ),
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    # pulls subcommand
    pulls_p = sub.add_parser(
        "pulls",
        help="Export all PR outcomes: number, author, timings, review count.",
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

    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        parser.error("--repo must be OWNER/NAME")
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", args.since):
            raise ValueError("--since must be YYYY-MM-DD")
        datetime.fromisoformat(args.since)
        if args.subcommand == "pulls":
            cmd_pulls(args)
        else:
            cmd_commits(args)
    except (ValueError, KeyError, TypeError, RuntimeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
