#!/usr/bin/env python3
"""Sample and evaluate code quality from actual git commits.

Requires repo checkouts (git repos on disk). Samples N commits per person,
analyzes diffs, and maps findings to CC-* rules from software-clean-code-standard.

Usage:
    python sample-code-quality.py --config config/report-config.json
    python sample-code-quality.py --repo ~/Projects/MyApp --person "Jane Doe" --sample-size 5
"""

import argparse
import ast
import json
import os
import random
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# CC-* Rule mapping for automated checks
# ---------------------------------------------------------------------------

CC_RULES = {
    "CC-FUN-01": "Each function MUST have one dominant responsibility",
    "CC-FUN-03": "Parameter lists SHOULD be small and cohesive",
    "CC-FUN-05": "Bug-prone duplication SHOULD be eliminated",
    "CC-FLOW-01": "Control flow SHOULD be shallow; prefer guard clauses",
    "CC-ERR-01": "Failures MUST be explicit and actionable; no silent failures",
    "CC-ERR-02": "Errors MUST carry context without leaking secrets",
    "CC-SEC-01": "Untrusted inputs MUST be validated at trust boundaries",
    "CC-SEC-03": "Secrets MUST NOT be hardcoded or logged",
    "CC-SEC-08": "Untrusted inputs MUST NOT be interpolated into interpreters",
    "CC-TST-01": "New behavior MUST be covered by tests",
    "CC-DOC-01": "Public interfaces MUST document contracts",
    "CC-DOC-04": "Commented-out code MUST NOT be committed",
    "CC-NAM-01": "Names MUST be intention-revealing and domain-accurate",
    "CC-NAM-03": "Units and time semantics MUST be explicit when relevant",
    "CC-PERF-02": "Obvious performance hazards MUST be avoided (N+1, O(n²))",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    rule_id: str
    priority: str  # P0, P1, P2, P3
    description: str
    file_path: str = ""
    line: int = 0

@dataclass
class CommitSample:
    commit_hash: str
    subject: str
    author: str
    date: str
    repo: str
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0
    diff_lines: int = 0
    has_test_files: bool = False
    has_security_files: bool = False
    message_quality_score: int = 0
    scope_assessment: str = ""
    findings: list = field(default_factory=list)
    complexity_before: int = 0
    complexity_after: int = 0

    def to_dict(self) -> dict:
        d = asdict(self)
        d["findings"] = [asdict(f) for f in self.findings]
        return d


# ---------------------------------------------------------------------------
# Git operations
# ---------------------------------------------------------------------------

def git_log_sample(repo_path: Path, person: str, sample_size: int,
                   skip_merges: bool = True, seed: int | None = None) -> list[dict]:
    """Get a random sample of commits by a person from a git repo."""
    cmd = ["git", "-C", str(repo_path), "log", "--all", "--format=%H|%an|%ae|%aI|%s", "--numstat"]
    if skip_merges:
        cmd.append("--no-merges")
    cmd.extend(["--author", person])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        return []

    # Parse git log output.
    commits = []
    current = None
    for line in result.stdout.split("\n"):
        parts = line.split("|", 4)
        if len(parts) >= 5 and len(parts[0]) == 40:
            if current:
                commits.append(current)
            current = {
                "hash": parts[0],
                "author_name": parts[1],
                "author_email": parts[2],
                "date": parts[3],
                "subject": parts[4],
                "files": [],
                "insertions": 0,
                "deletions": 0,
            }
        elif current and "\t" in line:
            file_parts = line.split("\t")
            if len(file_parts) == 3:
                ins = int(file_parts[0]) if file_parts[0] != "-" else 0
                dels = int(file_parts[1]) if file_parts[1] != "-" else 0
                current["files"].append(file_parts[2])
                current["insertions"] += ins
                current["deletions"] += dels
    if current:
        commits.append(current)

    # Random sample.
    if seed is not None:
        random.seed(seed)
    if len(commits) <= sample_size:
        return commits
    return random.sample(commits, sample_size)


def git_show_diff(repo_path: Path, commit_hash: str, max_lines: int = 300) -> str:
    """Get the diff for a specific commit."""
    cmd = ["git", "-C", str(repo_path), "show", "--format=", "--diff-filter=ACMR",
           "-U3", commit_hash]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return ""
    lines = result.stdout.split("\n")
    if len(lines) > max_lines:
        return "\n".join(lines[:max_lines]) + f"\n... (truncated, {len(lines)} total lines)"
    return result.stdout


def git_show_file(repo_path: Path, commit_hash: str, file_path: str) -> str:
    """Get file content at a specific commit."""
    cmd = ["git", "-C", str(repo_path), "show", f"{commit_hash}:{file_path}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return result.stdout if result.returncode == 0 else ""


def git_show_file_before(repo_path: Path, commit_hash: str, file_path: str) -> str:
    """Get file content before a specific commit."""
    cmd = ["git", "-C", str(repo_path), "show", f"{commit_hash}~1:{file_path}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return result.stdout if result.returncode == 0 else ""


# ---------------------------------------------------------------------------
# Analysis: Python AST complexity
# ---------------------------------------------------------------------------

def compute_cyclomatic_complexity(source: str) -> int:
    """Compute cyclomatic complexity of Python source using AST."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0

    complexity = 1  # Base complexity.
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1
        elif isinstance(node, ast.Assert):
            complexity += 1
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            complexity += 1
    return complexity


def compute_max_nesting(source: str) -> int:
    """Compute maximum nesting depth of Python source."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0

    max_depth = 0

    def walk(node, depth=0):
        nonlocal max_depth
        if isinstance(node, (ast.If, ast.While, ast.For, ast.With, ast.Try, ast.ExceptHandler)):
            depth += 1
            max_depth = max(max_depth, depth)
        for child in ast.iter_child_nodes(node):
            walk(child, depth)

    walk(tree)
    return max_depth


# ---------------------------------------------------------------------------
# Analysis: Diff-based checks
# ---------------------------------------------------------------------------

TEST_PATH_PATTERNS = re.compile(
    r"(test[s]?/|__tests__/|\.test\.|\.spec\.|_test\.|_spec\.)", re.IGNORECASE
)
SECURITY_PATH_PATTERNS = re.compile(
    r"(auth/|security/|crypto/|middleware/|\.env|secrets/|credentials/|jwt/|oauth/)", re.IGNORECASE
)
HARDCODED_SECRET_PATTERNS = re.compile(
    r"""(password\s*=\s*['"][^'"]{4,}|api_key\s*=\s*['"][^'"]{4,}|secret\s*=\s*['"][^'"]{4,}|"""
    r"""token\s*=\s*['"][^'"]{4,}|AKIA[0-9A-Z]{16})""",
    re.IGNORECASE,
)
SQL_INTERPOLATION_RE = re.compile(
    r"""(f['"].*?(SELECT|INSERT|UPDATE|DELETE|DROP).*?{|"""
    r"""['"].*?(SELECT|INSERT|UPDATE|DELETE|DROP).*?%s.*?%|"""
    r"""\.format\(.*?(SELECT|INSERT|UPDATE|DELETE))""",
    re.IGNORECASE,
)
COMMENTED_CODE_RE = re.compile(r"^\+\s*#\s*(def |class |import |from |if |for |while |return )")
EMPTY_EXCEPT_RE = re.compile(r"except.*:\s*(pass|\.\.\.)\s*$")
BARE_EXCEPT_RE = re.compile(r"except\s*:")


def analyze_diff(diff: str, files: list[str]) -> list[Finding]:
    """Analyze a commit diff for CC-* rule violations."""
    findings = []
    added_lines = [l for l in diff.split("\n") if l.startswith("+") and not l.startswith("+++")]

    # CC-SEC-03: Hardcoded secrets.
    for i, line in enumerate(added_lines):
        if HARDCODED_SECRET_PATTERNS.search(line):
            findings.append(Finding(
                rule_id="CC-SEC-03",
                priority="P0",
                description="Potential hardcoded secret or credential in added code",
                line=i,
            ))

    # CC-SEC-08: SQL interpolation.
    for i, line in enumerate(added_lines):
        if SQL_INTERPOLATION_RE.search(line):
            findings.append(Finding(
                rule_id="CC-SEC-08",
                priority="P0",
                description="Potential SQL injection via string interpolation",
                line=i,
            ))

    # CC-ERR-01: Empty except / bare except.
    for i, line in enumerate(added_lines):
        stripped = line.lstrip("+").strip()
        if EMPTY_EXCEPT_RE.match(stripped):
            findings.append(Finding(
                rule_id="CC-ERR-01",
                priority="P1",
                description="Silent failure: empty except block (pass/...)",
                line=i,
            ))
        elif BARE_EXCEPT_RE.match(stripped):
            findings.append(Finding(
                rule_id="CC-ERR-01",
                priority="P1",
                description="Bare except catches all exceptions including SystemExit/KeyboardInterrupt",
                line=i,
            ))

    # CC-DOC-04: Commented-out code.
    commented_code_count = sum(1 for l in added_lines if COMMENTED_CODE_RE.match(l))
    if commented_code_count >= 3:
        findings.append(Finding(
            rule_id="CC-DOC-04",
            priority="P3",
            description=f"{commented_code_count} lines of commented-out code added",
        ))

    # CC-TST-01: New code without tests.
    has_test_files = any(TEST_PATH_PATTERNS.search(f) for f in files)
    code_files = [f for f in files if not TEST_PATH_PATTERNS.search(f)
                  and f.endswith((".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".cs"))]
    if code_files and not has_test_files and len(added_lines) > 20:
        findings.append(Finding(
            rule_id="CC-TST-01",
            priority="P1",
            description=f"Code changes in {len(code_files)} file(s) without corresponding test changes",
        ))

    return findings


def analyze_python_file(before_source: str, after_source: str, file_path: str) -> list[Finding]:
    """Analyze a Python file for CC-* violations using AST."""
    findings = []

    # Complexity analysis.
    before_cc = compute_cyclomatic_complexity(before_source) if before_source else 0
    after_cc = compute_cyclomatic_complexity(after_source)

    if after_cc > before_cc + 5:
        findings.append(Finding(
            rule_id="CC-FLOW-01",
            priority="P2",
            description=f"Cyclomatic complexity increased significantly: {before_cc} → {after_cc}",
            file_path=file_path,
        ))

    # Nesting depth.
    max_nest = compute_max_nesting(after_source)
    if max_nest > 4:
        findings.append(Finding(
            rule_id="CC-FLOW-01",
            priority="P2",
            description=f"Deep nesting detected: {max_nest} levels",
            file_path=file_path,
        ))

    # Function length.
    try:
        tree = ast.parse(after_source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = getattr(node, "end_lineno", None)
                start = node.lineno
                if end and (end - start) > 50:
                    findings.append(Finding(
                        rule_id="CC-FUN-01",
                        priority="P2",
                        description=f"Long function '{node.name}': {end - start} lines",
                        file_path=file_path,
                        line=start,
                    ))
                # Parameter count.
                params = len(node.args.args) + len(node.args.posonlyargs) + len(node.args.kwonlyargs)
                if params > 5:
                    findings.append(Finding(
                        rule_id="CC-FUN-03",
                        priority="P2",
                        description=f"Function '{node.name}' has {params} parameters",
                        file_path=file_path,
                        line=start,
                    ))
    except SyntaxError:
        pass

    return findings


# ---------------------------------------------------------------------------
# Commit message quality
# ---------------------------------------------------------------------------

CONVENTIONAL_RE = re.compile(r"^(feat|fix|refactor|test|docs|chore|style|perf|ci|build)(\(.+\))?: .+")
IMPERATIVE_VERBS = {
    "add", "fix", "update", "remove", "refactor", "implement", "change",
    "create", "delete", "move", "rename", "extract", "improve", "replace",
    "merge", "revert", "bump", "set", "use", "handle", "support", "enable",
    "disable", "configure", "integrate", "migrate", "optimize", "simplify",
}
GENERIC_SUBJECTS = {"update", "fix", "changes", "wip", "temp", "misc", "stuff"}


def score_message_quality(subject: str) -> tuple[int, str]:
    """Score commit message quality (0-5) and return assessment."""
    score = 0
    notes = []
    if len(subject) >= 10:
        score += 1
    else:
        notes.append("too short")
    if CONVENTIONAL_RE.match(subject):
        score += 1
        notes.append("conventional format")
    first_word = subject.split("(")[0].split(":")[0].split(" ")[0].lower()
    if first_word in IMPERATIVE_VERBS:
        score += 1
    else:
        notes.append("no imperative verb")
    if len(subject) > 30 and subject.lower().strip() not in GENERIC_SUBJECTS:
        score += 2
        notes.append("descriptive")
    elif len(subject) > 20 and subject.lower().strip() not in GENERIC_SUBJECTS:
        score += 1
    if subject.lower().strip() in GENERIC_SUBJECTS:
        notes.append("generic")
    return score, "; ".join(notes) if notes else "good"


# ---------------------------------------------------------------------------
# Main sampling pipeline
# ---------------------------------------------------------------------------

def sample_person(repo_path: Path, person: str, sample_size: int,
                  max_diff_lines: int, skip_merges: bool, seed: int | None,
                  ast_extensions: list[str]) -> list[CommitSample]:
    """Sample and analyze commits for one person in one repo."""
    commits = git_log_sample(repo_path, person, sample_size, skip_merges, seed)
    samples = []

    for commit_data in commits:
        diff = git_show_diff(repo_path, commit_data["hash"], max_diff_lines)
        files = commit_data.get("files", [])
        msg_score, msg_assessment = score_message_quality(commit_data["subject"])

        sample = CommitSample(
            commit_hash=commit_data["hash"][:12],
            subject=commit_data["subject"],
            author=commit_data["author_name"],
            date=commit_data["date"][:10],
            repo=repo_path.name,
            files_changed=len(files),
            insertions=commit_data["insertions"],
            deletions=commit_data["deletions"],
            diff_lines=len(diff.split("\n")),
            has_test_files=any(TEST_PATH_PATTERNS.search(f) for f in files),
            has_security_files=any(SECURITY_PATH_PATTERNS.search(f) for f in files),
            message_quality_score=msg_score,
            scope_assessment=msg_assessment,
        )

        # Diff-based analysis.
        findings = analyze_diff(diff, files)

        # AST analysis for supported file types.
        py_files = [f for f in files if any(f.endswith(ext) for ext in ast_extensions)]
        total_before_cc = 0
        total_after_cc = 0
        for py_file in py_files[:5]:  # Limit to avoid timeout.
            before = git_show_file_before(repo_path, commit_data["hash"], py_file)
            after = git_show_file(repo_path, commit_data["hash"], py_file)
            if after:
                findings.extend(analyze_python_file(before, after, py_file))
                total_before_cc += compute_cyclomatic_complexity(before)
                total_after_cc += compute_cyclomatic_complexity(after)

        sample.complexity_before = total_before_cc
        sample.complexity_after = total_after_cc
        sample.findings = findings
        samples.append(sample)

    return samples


def main():
    parser = argparse.ArgumentParser(
        description="Sample and evaluate code quality from git commits."
    )
    parser.add_argument("--config", type=Path, help="Path to config JSON file")
    parser.add_argument("--repo", type=Path, help="Path to git repo (overrides config)")
    parser.add_argument("--person", help="Person name to sample (overrides config)")
    parser.add_argument("--sample-size", type=int, default=5, help="Commits per person (default: 5)")
    parser.add_argument("--output", type=Path, help="Output path for sample JSON")
    args = parser.parse_args()

    # Load config.
    config = {}
    config_dir = Path(".")
    if args.config:
        config_dir = args.config.parent
        with open(args.config) as f:
            config = json.load(f)

    sampling_config = config.get("quality_sampling", {})
    sample_size = args.sample_size or sampling_config.get("sample_size_per_person", 5)
    max_diff_lines = sampling_config.get("max_diff_lines_per_commit", 300)
    skip_merges = sampling_config.get("skip_merge_commits", True)
    seed = sampling_config.get("seed")
    ast_extensions = sampling_config.get("supported_ast_extensions", [".py"])

    # Determine repo roots.
    repo_roots = []
    if args.repo:
        repo_roots = [args.repo]
    else:
        for root in config.get("repo_roots", []):
            resolved = Path(root).expanduser().resolve()
            if resolved.exists():
                repo_roots.append(resolved)

    if not repo_roots:
        print("No repo roots specified. Use --repo or set repo_roots in config.", file=sys.stderr)
        sys.exit(1)

    # Determine persons.
    persons = []
    if args.person:
        persons = [args.person]
    else:
        persons = config.get("target_persons", [])

    if not persons:
        print("No persons specified. Use --person or set target_persons in config.", file=sys.stderr)
        sys.exit(1)

    # Output path.
    output_path = args.output
    if not output_path:
        output_dir = config_dir / config.get("output_profiles", "../derived/")
        output_dir = output_dir.parent
        output_path = output_dir / "sample-quality.json"

    # Run sampling.
    all_samples = {}
    for person in persons:
        print(f"\nSampling {sample_size} commits for {person}:")
        person_samples = []
        for repo_path in repo_roots:
            samples = sample_person(
                repo_path, person, sample_size, max_diff_lines,
                skip_merges, seed, ast_extensions,
            )
            person_samples.extend(samples)
            for s in samples:
                finding_count = len(s.findings)
                cc_delta = s.complexity_after - s.complexity_before
                print(f"  {s.commit_hash} {s.date} | {s.files_changed} files, "
                      f"+{s.insertions}/-{s.deletions} | "
                      f"msg:{s.message_quality_score}/5 | "
                      f"findings:{finding_count} | cc_delta:{cc_delta:+d}")

        all_samples[person] = [s.to_dict() for s in person_samples]

        # Summary.
        if person_samples:
            total_findings = sum(len(s.findings) for s in person_samples)
            p0_p1 = sum(
                1 for s in person_samples for f in s.findings if f.priority in ("P0", "P1")
            )
            avg_msg = sum(s.message_quality_score for s in person_samples) / len(person_samples)
            has_test = sum(1 for s in person_samples if s.has_test_files)
            print(f"  Summary: {total_findings} findings ({p0_p1} P0/P1), "
                  f"avg msg quality: {avg_msg:.1f}/5, "
                  f"commits with tests: {has_test}/{len(person_samples)}")

    output = {
        "generated_at": datetime.now().isoformat(),
        "config": {
            "sample_size": sample_size,
            "max_diff_lines": max_diff_lines,
            "skip_merges": skip_merges,
            "ast_extensions": ast_extensions,
        },
        "persons": all_samples,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nSample quality results written to {output_path}")


if __name__ == "__main__":
    main()
