#!/usr/bin/env python3
"""Extract a deterministic code profile from a single repository."""

from __future__ import annotations

import argparse
import ast
import json
import re
from datetime import datetime, timezone
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".build",
    ".swiftpm",
    "node_modules",
    "dist",
    "build",
    ".next",
    "vendor",
    ".archive",
    ".venv",
    "venv",
    "__pycache__",
    "coverage",
    ".turbo",
    "DerivedData",
    "Pods",
    "Carthage",
    "SourcePackages",
    "xcuserdata",
}

LANGUAGE_BY_SUFFIX = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TSX",
    ".cs": "C#",
    ".swift": "Swift",
}

CALL_KEYWORDS = {
    "if",
    "for",
    "while",
    "switch",
    "catch",
    "return",
    "new",
    "typeof",
    "await",
    "nameof",
    "assert",
    "guard",
    "defer",
    "init",
}

IMPORT_RE = re.compile(r'^\s*import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE)
REQUIRE_RE = re.compile(r'require\([\'"]([^\'"]+)[\'"]\)')
USING_RE = re.compile(r'^\s*using\s+([A-Za-z0-9_.]+)\s*;', re.MULTILINE)
JS_CLASS_RE = re.compile(r'\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\b(?:\s+extends\s+([A-Za-z_][A-Za-z0-9_]*))?')
CS_CLASS_RE = re.compile(r'\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\b(?:\s*:\s*([A-Za-z_][A-Za-z0-9_]*))?')
SWIFT_IMPORT_RE = re.compile(r'^\s*import\s+([A-Za-z0-9_.]+)', re.MULTILINE)
SWIFT_TYPE_RE = re.compile(
    r'^\s*(?:@\w+(?:\([^)]*\))?\s*)*'
    r'(?:(?:public|private|fileprivate|internal|open|final|indirect|nonisolated)\s+)*'
    r'(class|struct|actor|enum|protocol)\s+([A-Za-z_][A-Za-z0-9_]*)\b'
    r'(?:\s*:\s*([^{]+))?',
    re.MULTILINE,
)
JS_FUNCTION_RE = re.compile(r'^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', re.MULTILINE)
JS_ARROW_RE = re.compile(r'^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', re.MULTILINE)
JS_METHOD_RE = re.compile(r'^\s*(?:public\s+|private\s+|protected\s+|static\s+|async\s+)*(?:get\s+|set\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\([^;]*\)\s*\{', re.MULTILINE)
SWIFT_FUNCTION_RE = re.compile(
    r'^\s*(?:@\w+(?:\([^)]*\))?\s*)*'
    r'(?:(?:public|private|fileprivate|internal|open|final|override|mutating|nonmutating|static|class|convenience|required)\s+)*'
    r'func\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(',
    re.MULTILINE,
)
CS_METHOD_RE = re.compile(
    r'^\s*(?:\[.*\]\s*)*(?:(?:public|private|protected|internal|static|async|virtual|override|sealed|partial|new|extern)\s+)+'
    r'[\w<>\[\],?.]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^;]*\)\s*\{',
    re.MULTILINE,
)
TEST_CASE_RE = re.compile(r'^\s*(?:test|it|describe)\s*\(\s*[\'"]([^\'"]+)[\'"]')
CALL_RE = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*\(')
ATTR_CALL_RE = re.compile(r'\.([A-Za-z_][A-Za-z0-9_]*)\s*\(')


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_id(text: str) -> str:
    return re.sub(r"[^a-z0-9._-]", "-", text.lower().strip()).strip("-")


def file_node_id(repo_id: str, rel_path: Path) -> str:
    return f"{repo_id}#file#{normalize_id(rel_path.as_posix())}"


def symbol_node_id(parent_id: str, symbol_type: str, label: str) -> str:
    return f"{parent_id}#{symbol_type}#{normalize_id(label)}"


def external_node_id(kind: str, label: str) -> str:
    return f"external#{kind}#{normalize_id(label)}"


def detect_file_kind(rel_path: Path) -> str:
    lowered = rel_path.as_posix().lower()
    parts = {part.lower() for part in rel_path.parts}
    if "__tests__" in parts or "tests" in parts or "specs" in parts:
        return "test"
    if lowered.endswith((".test.js", ".test.ts", ".test.tsx", ".spec.js", ".spec.ts", ".spec.tsx", "_test.py", "_test.cs")):
        return "test"
    if rel_path.name.lower().startswith("test_"):
        return "test"
    return "source"


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def iter_code_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path.relative_to(repo_root)):
            continue
        if path.suffix.lower() in LANGUAGE_BY_SUFFIX:
            files.append(path)
    return sorted(files)


def add_relation(relations: list[dict], seen: set[tuple[str, str, str]], source: str, target: str, relation: str, group: str, confidence: float, notes: str | None = None) -> None:
    key = (source, target, relation)
    if key in seen:
        return
    seen.add(key)
    payload = {
        "source": source,
        "target": target,
        "relation": relation,
        "group": group,
        "confidence": round(confidence, 3),
    }
    if notes:
        payload["notes"] = notes
    relations.append(payload)


def is_test_name(name: str) -> bool:
    lowered = name.lower()
    return lowered.startswith("test") or lowered.endswith("test")


def resolve_relative_import(repo_root: Path, current_file: Path, raw_target: str) -> Path | None:
    if not raw_target.startswith("."):
        return None
    base = current_file.parent
    remainder = raw_target
    while remainder.startswith("../"):
        base = base.parent
        remainder = remainder[3:]
    if remainder.startswith("./"):
        remainder = remainder[2:]
    candidate_base = (base / remainder).resolve()
    candidates = [
        candidate_base,
        candidate_base.with_suffix(".ts"),
        candidate_base.with_suffix(".tsx"),
        candidate_base.with_suffix(".js"),
        candidate_base.with_suffix(".jsx"),
        candidate_base.with_suffix(".py"),
        candidate_base.with_suffix(".cs"),
        candidate_base / "index.ts",
        candidate_base / "index.tsx",
        candidate_base / "index.js",
        candidate_base / "index.jsx",
        candidate_base / "__init__.py",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


class PythonAnalyzer(ast.NodeVisitor):
    def __init__(self, repo_root: Path, repo_id: str, file_path: Path, rel_path: Path, file_id: str, file_kind: str) -> None:
        self.repo_root = repo_root
        self.repo_id = repo_id
        self.file_path = file_path
        self.rel_path = rel_path
        self.file_id = file_id
        self.file_kind = file_kind
        self.symbols: list[dict] = []
        self.relations: list[dict] = []
        self.relation_seen: set[tuple[str, str, str]] = set()
        self.symbol_stack: list[tuple[str, str]] = []
        self.class_stack: list[str] = []
        self.pending_calls: list[tuple[str, str, bool]] = []
        self.pending_inherits: list[tuple[str, str]] = []
        self.label_index: dict[str, list[str]] = {}

    def add_symbol(self, symbol_type: str, label: str, parent_id: str, node: ast.AST) -> str:
        symbol_id = symbol_node_id(parent_id, symbol_type, label)
        line_end = getattr(node, "end_lineno", getattr(node, "lineno", None))
        entry = {
            "id": symbol_id,
            "type": symbol_type,
            "label": label,
            "path": self.rel_path.as_posix(),
            "language": "Python",
            "parent_id": parent_id,
            "line_start": getattr(node, "lineno", None),
            "line_end": line_end,
            "confidence": 0.97,
        }
        self.symbols.append(entry)
        self.label_index.setdefault(label, []).append(symbol_id)
        add_relation(self.relations, self.relation_seen, parent_id, symbol_id, "defines", "structural", 0.98)
        return symbol_id

    def current_parent(self) -> str:
        if self.class_stack:
            return self.class_stack[-1]
        return self.file_id

    def current_symbol(self) -> tuple[str, str] | None:
        if not self.symbol_stack:
            return None
        return self.symbol_stack[-1]

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            target = self.resolve_import(alias.name, 0)
            add_relation(self.relations, self.relation_seen, self.file_id, target, "imports", "dependency", 0.92)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        target = self.resolve_import(module, node.level)
        add_relation(self.relations, self.relation_seen, self.file_id, target, "imports", "dependency", 0.9)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_id = self.add_symbol("class", node.name, self.file_id, node)
        self.class_stack.append(class_id)
        self.symbol_stack.append((class_id, "class"))
        for base in node.bases:
            base_name = self.extract_name(base)
            if base_name:
                self.pending_inherits.append((class_id, base_name))
        self.generic_visit(node)
        self.symbol_stack.pop()
        self.class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_callable(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_callable(node)

    def _visit_callable(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        symbol_type = "method" if self.class_stack else "function"
        if self.file_kind == "test" and is_test_name(node.name):
            symbol_type = "test"
        parent_id = self.current_parent()
        symbol_id = self.add_symbol(symbol_type, node.name, parent_id, node)
        self.symbol_stack.append((symbol_id, symbol_type))
        self.generic_visit(node)
        self.symbol_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        current = self.current_symbol()
        if current is not None:
            symbol_id, symbol_type = current
            call_name = self.extract_name(node.func)
            if call_name:
                self.pending_calls.append((symbol_id, call_name, symbol_type == "test"))
        self.generic_visit(node)

    def resolve_import(self, module: str, level: int) -> str:
        if level > 0:
            base = self.file_path.parent
            for _ in range(level - 1):
                base = base.parent
            candidate_base = base
            if module:
                candidate_base = candidate_base.joinpath(*module.split("."))
            for candidate in (
                candidate_base.with_suffix(".py"),
                candidate_base / "__init__.py",
            ):
                if candidate.exists():
                    return file_node_id(self.repo_id, candidate.relative_to(self.repo_root))
        else:
            candidate_base = self.repo_root.joinpath(*module.split(".")) if module else self.repo_root
            for candidate in (
                candidate_base.with_suffix(".py"),
                candidate_base / "__init__.py",
            ):
                if candidate.exists():
                    return file_node_id(self.repo_id, candidate.relative_to(self.repo_root))
        label = module or "relative-import"
        return external_node_id("import", label)

    @staticmethod
    def extract_name(node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return None

    def finalize(self) -> tuple[list[dict], list[dict]]:
        for source_id, target_label, is_test_caller in self.pending_calls:
            resolved_target = self.resolve_symbol_label(target_label, "call")
            relation = "tests" if is_test_caller else "calls"
            group = "behavioral" if is_test_caller else "behavioral"
            confidence = 0.82 if relation == "calls" else 0.72
            add_relation(self.relations, self.relation_seen, source_id, resolved_target, relation, group, confidence)
        for class_id, base_label in self.pending_inherits:
            resolved_target = self.resolve_symbol_label(base_label, "inherit")
            add_relation(self.relations, self.relation_seen, class_id, resolved_target, "inherits", "semantic", 0.8)
        return self.symbols, self.relations

    def resolve_symbol_label(self, label: str, kind: str) -> str:
        matches = self.label_index.get(label, [])
        if len(matches) == 1:
            return matches[0]
        return external_node_id(kind, label)


def extract_brace_calls(line: str) -> list[str]:
    names = set(ATTR_CALL_RE.findall(line))
    names.update(CALL_RE.findall(line))
    cleaned = []
    for name in names:
        if name in CALL_KEYWORDS:
            continue
        cleaned.append(name)
    return sorted(set(cleaned))


def parse_swift_inheritance_targets(raw_clause: str | None) -> list[str]:
    if not raw_clause:
        return []
    targets: list[str] = []
    for candidate in raw_clause.split(","):
        cleaned = candidate.strip()
        if not cleaned:
            continue
        cleaned = cleaned.split("where", 1)[0].strip()
        cleaned = cleaned.split("<", 1)[0].strip()
        cleaned = cleaned.split("(", 1)[0].strip()
        cleaned = cleaned.split(":", 1)[0].strip()
        if not cleaned:
            continue
        tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", cleaned)
        if tokens:
            targets.append(tokens[-1])
    return targets


def analyze_heuristic_file(repo_root: Path, repo_id: str, file_path: Path, rel_path: Path, file_id: str, language: str, file_kind: str) -> tuple[str, list[dict], list[dict]]:
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    symbols: list[dict] = []
    relations: list[dict] = []
    relation_seen: set[tuple[str, str, str]] = set()
    label_index: dict[str, list[str]] = {}
    pending_calls: list[tuple[str, str, str]] = []
    pending_inherits: list[tuple[str, str]] = []
    file_kind = detect_file_kind(rel_path)

    lines = content.splitlines()
    brace_depth = 0
    class_stack: list[tuple[str, int]] = []
    symbol_context: list[tuple[str, str, int]] = []

    def add_symbol(symbol_type: str, label: str, parent_id: str, line_no: int, confidence: float) -> str:
        symbol_id = symbol_node_id(parent_id, symbol_type, label)
        entry = {
            "id": symbol_id,
            "type": symbol_type,
            "label": label,
            "path": rel_path.as_posix(),
            "language": language,
            "parent_id": parent_id,
            "line_start": line_no,
            "line_end": line_no,
            "confidence": confidence,
        }
        if not any(existing["id"] == symbol_id for existing in symbols):
            symbols.append(entry)
            label_index.setdefault(label, []).append(symbol_id)
            add_relation(relations, relation_seen, parent_id, symbol_id, "defines", "structural", min(confidence + 0.1, 0.95))
        return symbol_id

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        open_count = line.count("{")
        close_count = line.count("}")
        if not stripped:
            brace_depth += open_count - close_count
            while symbol_context and brace_depth < symbol_context[-1][2]:
                symbol_context.pop()
            while class_stack and brace_depth < class_stack[-1][1]:
                class_stack.pop()
            continue

        if language in {"JavaScript", "TypeScript", "TSX"}:
            for target in IMPORT_RE.findall(line):
                resolved = resolve_relative_import(repo_root, file_path, target)
                target_id = file_node_id(repo_id, resolved.relative_to(repo_root)) if resolved else external_node_id("import", target)
                add_relation(relations, relation_seen, file_id, target_id, "imports", "dependency", 0.78)
            for target in REQUIRE_RE.findall(line):
                resolved = resolve_relative_import(repo_root, file_path, target)
                target_id = file_node_id(repo_id, resolved.relative_to(repo_root)) if resolved else external_node_id("import", target)
                add_relation(relations, relation_seen, file_id, target_id, "imports", "dependency", 0.72)

        if language == "C#":
            for target in USING_RE.findall(line):
                add_relation(relations, relation_seen, file_id, external_node_id("import", target), "imports", "dependency", 0.7)
        elif language == "Swift":
            for target in SWIFT_IMPORT_RE.findall(line):
                add_relation(relations, relation_seen, file_id, external_node_id("import", target), "imports", "dependency", 0.74)

        if language in {"JavaScript", "TypeScript", "TSX"}:
            class_match = JS_CLASS_RE.search(line)
        elif language == "C#":
            class_match = CS_CLASS_RE.search(line)
        else:
            class_match = SWIFT_TYPE_RE.search(line) if language == "Swift" else None
        if class_match:
            class_name = class_match.group(2) if language == "Swift" else class_match.group(1)
            parent_id = file_id
            class_id = add_symbol("class", class_name, parent_id, line_no, 0.66)
            if language == "Swift":
                for base_name in parse_swift_inheritance_targets(class_match.group(3)):
                    pending_inherits.append((class_id, base_name))
            else:
                base_name = class_match.group(2)
                if base_name:
                    pending_inherits.append((class_id, base_name))

        function_match = None
        if language in {"JavaScript", "TypeScript", "TSX"}:
            function_match = JS_FUNCTION_RE.match(line) or JS_ARROW_RE.match(line) or JS_METHOD_RE.match(line)
        elif language == "C#":
            function_match = CS_METHOD_RE.match(line)
        elif language == "Swift":
            function_match = SWIFT_FUNCTION_RE.match(line)

        test_case_match = TEST_CASE_RE.match(line) if file_kind == "test" and language in {"JavaScript", "TypeScript", "TSX"} else None
        if function_match:
            label = function_match.group(1)
            class_parent = class_stack[-1][0] if class_stack else None
            symbol_type = "method" if class_parent else "function"
            if file_kind == "test" and is_test_name(label):
                symbol_type = "test"
            parent_id = class_parent or file_id
            symbol_id = add_symbol(symbol_type, label, parent_id, line_no, 0.6 if symbol_type == "function" else 0.58)
            symbol_context.append((symbol_id, symbol_type, brace_depth + max(open_count - close_count, 1)))
        elif test_case_match:
            label = test_case_match.group(1) or f"test-{line_no}"
            symbol_id = add_symbol("test", label, file_id, line_no, 0.56)
            symbol_context.append((symbol_id, "test", brace_depth + max(open_count - close_count, 1)))

        active_symbol = symbol_context[-1] if symbol_context else None
        if active_symbol:
            source_id, symbol_type, _ = active_symbol
            relation_name = "tests" if symbol_type == "test" else "calls"
            for target_name in extract_brace_calls(line):
                pending_calls.append((source_id, target_name, relation_name))
        post_depth = brace_depth + open_count - close_count

        if class_match and open_count > close_count:
            class_label = class_match.group(2) if language == "Swift" else class_match.group(1)
            class_id = symbol_node_id(file_id, "class", class_label)
            class_stack.append((class_id, max(post_depth, brace_depth + 1)))

        brace_depth = post_depth

        while symbol_context and brace_depth < symbol_context[-1][2]:
            symbol_context.pop()
        while class_stack and brace_depth < class_stack[-1][1]:
            class_stack.pop()

    for source_id, target_name, relation_name in pending_calls:
        matches = label_index.get(target_name, [])
        target_id = matches[0] if len(matches) == 1 else external_node_id("call", target_name)
        confidence = 0.58 if relation_name == "calls" else 0.52
        add_relation(relations, relation_seen, source_id, target_id, relation_name, "behavioral", confidence)

    for class_id, base_name in pending_inherits:
        matches = label_index.get(base_name, [])
        target_id = matches[0] if len(matches) == 1 else external_node_id("inherit", base_name)
        add_relation(relations, relation_seen, class_id, target_id, "inherits", "semantic", 0.62)

    return "heuristic", symbols, relations


def analyze_python_file(repo_root: Path, repo_id: str, file_path: Path, rel_path: Path, file_id: str, file_kind: str) -> tuple[str, list[dict], list[dict]]:
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return "error", [], []
    analyzer = PythonAnalyzer(repo_root, repo_id, file_path, rel_path, file_id, file_kind)
    analyzer.visit(tree)
    symbols, relations = analyzer.finalize()
    return "parsed", symbols, relations


def scan_repo(repo_root: Path) -> dict:
    repo_root = repo_root.expanduser().resolve()
    repo_id = normalize_id(repo_root.name)
    files: list[dict] = []
    symbols: list[dict] = []
    relations: list[dict] = []
    evidence: list[dict] = []
    languages: list[str] = []
    relation_seen: set[tuple[str, str, str]] = set()

    for file_path in iter_code_files(repo_root):
        rel_path = file_path.relative_to(repo_root)
        language = LANGUAGE_BY_SUFFIX[file_path.suffix.lower()]
        if language not in languages:
            languages.append(language)
        file_kind = detect_file_kind(rel_path)
        file_id = file_node_id(repo_id, rel_path)

        parse_status = "unsupported"
        extracted_symbols: list[dict] = []
        extracted_relations: list[dict] = []
        if language == "Python":
            parse_status, extracted_symbols, extracted_relations = analyze_python_file(repo_root, repo_id, file_path, rel_path, file_id, file_kind)
        elif language in {"JavaScript", "TypeScript", "TSX", "C#", "Swift"}:
            parse_status, extracted_symbols, extracted_relations = analyze_heuristic_file(repo_root, repo_id, file_path, rel_path, file_id, language, file_kind)

        file_confidence = {
            "parsed": 0.96,
            "heuristic": 0.62,
            "unsupported": 0.35,
            "error": 0.25,
            "skipped": 0.1,
        }[parse_status]

        files.append(
            {
                "id": file_id,
                "path": rel_path.as_posix(),
                "language": language,
                "kind": file_kind,
                "parse_status": parse_status,
                "confidence": file_confidence,
            }
        )
        if len(evidence) < 25:
            evidence.append({"path": rel_path.as_posix(), "reason": f"{parse_status} code file"})

        add_relation(relations, relation_seen, repo_id, file_id, "contains", "structural", 1.0)

        for symbol in extracted_symbols:
            if not any(existing["id"] == symbol["id"] for existing in symbols):
                symbols.append(symbol)
        for relation in extracted_relations:
            add_relation(
                relations,
                relation_seen,
                relation["source"],
                relation["target"],
                relation["relation"],
                relation["group"],
                relation["confidence"],
                relation.get("notes"),
            )

    parsed_files = sum(1 for entry in files if entry["parse_status"] == "parsed")
    heuristic_files = sum(1 for entry in files if entry["parse_status"] == "heuristic")
    summary = (
        f"{repo_root.name} has {len(files)} code file(s), {len(symbols)} symbol node(s), and "
        f"{len(relations)} relation(s); {parsed_files} file(s) parsed strongly and {heuristic_files} file(s) parsed heuristically."
    )

    supported_files = [entry for entry in files if entry["parse_status"] in {"parsed", "heuristic"}]
    confidence_score = round(sum(entry["confidence"] for entry in supported_files) / max(len(files), 1), 3) if files else 0.0

    return {
        "repo_id": repo_id,
        "repo_name": repo_root.name,
        "repo_path": str(repo_root),
        "languages": languages,
        "files": files,
        "symbols": symbols,
        "relations": relations,
        "summary": summary,
        "evidence": evidence,
        "confidence_score": confidence_score,
        "last_scanned_at": now_iso(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="Path to the repository root")
    args = parser.parse_args()
    print(json.dumps(scan_repo(Path(args.repo)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
