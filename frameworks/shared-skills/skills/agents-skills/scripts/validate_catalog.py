#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from audit_skill_metadata import audit_skill, skill_dirs
from validate_skill import find_transient_dirs, validate_skill_dir


@dataclass
class CatalogIssue:
    severity: str
    rule_id: str
    path: Path
    message: str


def audit_catalog(catalog_root: Path) -> list[CatalogIssue]:
    issues: list[CatalogIssue] = []
    for row in (audit_skill(skill_dir) for skill_dir in skill_dirs(catalog_root)):
        skill_path = catalog_root / str(row["skill"]) / "SKILL.md"
        for warning in row["warnings"]:
            issues.append(
                CatalogIssue(
                    severity="warning",
                    rule_id="metadata",
                    path=skill_path,
                    message=str(warning),
                )
            )
    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate every top-level skill in a catalog.")
    parser.add_argument("catalog_root", help="Path to the skills catalog root")
    parser.add_argument("--check-urls", action="store_true", help="Attempt to fetch HTTPS URLs from sources.json")
    parser.add_argument(
        "--strict-transients",
        action="store_true",
        help="Fail if transient directories such as .venv or __pycache__ exist inside any skill bundle",
    )
    parser.add_argument("--skip-semantic", action="store_true", help="Skip catalog-wide semantic audit checks")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of Markdown")
    return parser.parse_args()


def top_level_skills(catalog_root: Path) -> list[Path]:
    return sorted(path for path in catalog_root.iterdir() if path.is_dir() and not path.name.startswith("."))


def main() -> int:
    args = parse_args()
    catalog_root = Path(args.catalog_root).resolve()
    skills = top_level_skills(catalog_root)

    summaries: list[dict[str, object]] = []
    transient_total = 0

    for skill_dir in skills:
        issues = validate_skill_dir(skill_dir, check_urls=args.check_urls)
        errors = [issue for issue in issues if issue.severity == "error"]
        warnings = [issue for issue in issues if issue.severity == "warning"]
        transients = find_transient_dirs(skill_dir)
        transient_total += len(transients)

        summaries.append(
            {
                "skill": skill_dir.name,
                "status": "FAIL" if errors else "WARN" if warnings else "PASS",
                "errors": len(errors),
                "warnings": len(warnings),
                "transient_dirs": [str(path.relative_to(catalog_root)) for path in transients],
                "issues": [
                    {
                        "severity": issue.severity,
                        "path": str(issue.path.relative_to(catalog_root)),
                        "message": issue.message,
                    }
                    for issue in issues
                ],
            }
        )

    fail_count = sum(1 for summary in summaries if summary["status"] == "FAIL")
    warn_count = sum(1 for summary in summaries if summary["status"] == "WARN")
    pass_count = sum(1 for summary in summaries if summary["status"] == "PASS")
    semantic_issues = [] if args.skip_semantic else audit_catalog(catalog_root)
    semantic_errors = [issue for issue in semantic_issues if issue.severity == "error"]
    semantic_warnings = [issue for issue in semantic_issues if issue.severity == "warning"]

    exit_code = 1 if fail_count or semantic_errors or (args.strict_transients and transient_total) else 0

    if args.json:
        payload = {
            "catalog_root": str(catalog_root),
            "skills": len(skills),
            "pass_count": pass_count,
            "warn_count": warn_count,
            "fail_count": fail_count,
            "transient_dir_count": transient_total,
            "strict_transients": args.strict_transients,
            "semantic_error_count": len(semantic_errors),
            "semantic_warning_count": len(semantic_warnings),
            "semantic_issues": [
                {
                    "severity": issue.severity,
                    "rule_id": issue.rule_id,
                    "path": str(issue.path.relative_to(catalog_root.parent)),
                    "message": issue.message,
                }
                for issue in semantic_issues
            ],
            "results": summaries,
        }
        print(json.dumps(payload, indent=2))
        return exit_code

    print("## Catalog Validation Summary")
    print()
    print(f"- Catalog: `{catalog_root}`")
    print(f"- Skills: {len(skills)}")
    print(f"- Pass: {pass_count}")
    print(f"- Warn: {warn_count}")
    print(f"- Fail: {fail_count}")
    print(f"- Transient dirs: {transient_total}")
    print(f"- Semantic errors: {len(semantic_errors)}")
    print(f"- Semantic warnings: {len(semantic_warnings)}")
    print()

    if fail_count:
        print("## Failing Skills")
        for summary in summaries:
            if summary["status"] != "FAIL":
                continue
            print(f"- `{summary['skill']}`: {summary['errors']} error(s), {summary['warnings']} warning(s)")
        print()

    if warn_count:
        print("## Warning Skills")
        for summary in summaries:
            if summary["status"] != "WARN":
                continue
            print(f"- `{summary['skill']}`: {summary['warnings']} warning(s)")
        print()

    if transient_total:
        print("## Transient Directories")
        for summary in summaries:
            transient_dirs = summary["transient_dirs"]
            if not transient_dirs:
                continue
            for transient_dir in transient_dirs:
                print(f"- `{summary['skill']}`: `{transient_dir}`")
        print()

    if semantic_errors:
        print("## Semantic Errors")
        for issue in semantic_errors:
            print(f"- [{issue.rule_id}] `{issue.path.relative_to(catalog_root.parent)}`: {issue.message}")
        print()

    if semantic_warnings:
        print("## Semantic Warnings")
        for issue in semantic_warnings:
            print(f"- [{issue.rule_id}] `{issue.path.relative_to(catalog_root.parent)}`: {issue.message}")
        print()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
