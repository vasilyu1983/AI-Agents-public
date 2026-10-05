#!/usr/bin/env python3
"""Export a bounded local git history to the contribution-profile CSV schema.

This fallback has no forge review or MR events. It writes an empty MR CSV with
the expected header so downstream scripts mark those signals unavailable.
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

COMMIT_FIELDS = (
    "repo commit_hash author_name author_email datetime weekday hour timezone subject "
    "files_changed insertions deletions is_merge is_move code_ins code_del test_ins test_del "
    "config_ins config_del docs_ins docs_del other_ins other_del"
).split()
MR_FIELDS = (
    "repo commit_hash merger_name merger_email datetime weekday hour timezone source_branch "
    "subject files_changed insertions deletions"
).split()
CODE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt",
    ".swift", ".c", ".cc", ".cpp", ".h", ".cs", ".rb", ".php", ".sql",
    ".css", ".scss", ".sh",
}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".xml", ".tf"}
DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".txt", ".adoc"}


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True,
                            capture_output=True, check=False)
    if result.returncode:
        raise ValueError(f"git {' '.join(args[:2])} failed: {result.stderr.strip()}")
    return result.stdout


def bucket(path: str) -> str:
    lower = path.lower()
    name = Path(lower).name
    if name.endswith((".lock", ".snap")) or any(part in lower.split("/") for part in
                                                 ("generated", "vendor", "node_modules")):
        return "other"
    if any(part in lower.split("/") for part in ("test", "tests", "spec", "__tests__")) or \
            name.endswith(("_test.py", ".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx")):
        return "test"
    ext = Path(lower).suffix
    if ext in CODE_EXTENSIONS:
        return "code"
    if ext in CONFIG_EXTENSIONS or name in ("dockerfile", ".env"):
        return "config"
    if ext in DOC_EXTENSIONS:
        return "docs"
    return "other"


def commit_row(repo: Path, sha: str) -> dict:
    raw = git(repo, "show", "--no-renames", "--no-ext-diff", "--no-textconv", "--numstat",
              "--format=%H%x1f%an%x1f%ae%x1f%aI%x1f%s%x1f%P", sha)
    lines = raw.splitlines()
    if not lines:
        raise ValueError(f"empty git show output for {sha}")
    meta = lines[0].split("\x1f")
    if len(meta) != 6 or meta[0] != sha:
        raise ValueError(f"malformed git show metadata for {sha}")
    timestamp = datetime.fromisoformat(meta[3])
    row = dict.fromkeys(COMMIT_FIELDS, 0)
    row.update(repo=repo.name, commit_hash=sha, author_name=meta[1], author_email=meta[2],
               datetime=meta[3], weekday=timestamp.strftime("%A"), hour=timestamp.hour,
               timezone=timestamp.strftime("%z"), subject=meta[4],
               is_merge=int(bool(meta[5].split()[1:])), is_move=0)
    for line in lines[1:]:
        if not line:
            continue
        cells = line.split("\t", 2)
        if len(cells) != 3:
            raise ValueError(f"malformed numstat row for {sha}: {line!r}")
        ins, dele, path = cells
        if ins == dele == "-":
            added = removed = 0
        elif ins.isdecimal() and dele.isdecimal():
            added, removed = int(ins), int(dele)
        else:
            raise ValueError(f"invalid numstat counts for {sha}: {line!r}")
        kind = bucket(path)
        row["files_changed"] += 1
        row["insertions"] += added
        row["deletions"] += removed
        row[f"{kind}_ins"] += added
        row[f"{kind}_del"] += removed
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--since", required=True, help="Inclusive ISO date (YYYY-MM-DD)")
    parser.add_argument("--out-commits", required=True, type=Path)
    parser.add_argument("--out-mr", required=True, type=Path)
    args = parser.parse_args()
    try:
        since = date.fromisoformat(args.since)
        if since > date.today():
            raise ValueError("--since is in the future")
        if args.out_commits.resolve() == args.out_mr.resolve():
            raise ValueError("output paths must differ")
        if args.out_commits.exists() or args.out_mr.exists():
            raise ValueError("output path already exists; choose new paths")
        repo = args.repo.resolve()
        if not repo.is_dir():
            raise ValueError(f"repo directory does not exist: {repo}")
        shas = git(repo, "rev-list", "--no-merges", f"--since={since.isoformat()}", "HEAD").splitlines()
        if not shas:
            raise ValueError(f"no commits since {since.isoformat()} in {repo}")
        rows = [commit_row(repo, sha) for sha in shas]
        for path in (args.out_commits, args.out_mr):
            path.parent.mkdir(parents=True, exist_ok=True)
        with args.out_commits.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=COMMIT_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        with args.out_mr.open("w", newline="") as handle:
            csv.DictWriter(handle, fieldnames=MR_FIELDS).writeheader()
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Exported {len(rows)} commits; MR events unavailable without forge data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
