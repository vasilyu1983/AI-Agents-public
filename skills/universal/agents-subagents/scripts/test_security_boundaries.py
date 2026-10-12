#!/usr/bin/env python3
"""Focused regressions for executable and supply-chain safety boundaries."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
HEADLESS = SCRIPT_DIR / "headless-review.sh"
TEARDOWN = SCRIPT_DIR / "teardown-team.sh"


class HeadlessReviewBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = HEADLESS.read_text(encoding="utf-8")

    def invocation(self) -> str:
        """The `claude -p` invocation with its line continuations flattened."""
        start = self.text.index("claude -p ")
        flattened = self.text[start:].replace("\\\n", " ")
        return flattened.split("\n", 1)[0]

    def test_review_agents_have_no_command_execution_authority(self) -> None:
        self.assertNotIn('"Bash"', self.text)
        self.assertNotIn("Bash(", self.text)
        self.assertIn('--allowedTools "Read,Grep,Glob,Agent"', self.invocation())

    def test_headless_review_loads_no_mcp_servers(self) -> None:
        # Without --strict-mcp-config, `claude -p` loads every configured MCP server and
        # injects each server's `instructions` into the system prompt of a session whose
        # user prompt already carries an untrusted diff. Assert on the invocation itself,
        # not on the file text, so a mention in a comment cannot satisfy the boundary.
        invocation = self.invocation()
        self.assertIn("--strict-mcp-config", invocation)
        # --strict-mcp-config only restricts MCP to servers named by --mcp-config; passing
        # none is what reduces the set to zero.
        self.assertNotIn("--mcp-config", invocation)

    def test_review_content_is_untrusted_and_target_is_worktree_bounded(self) -> None:
        self.assertIn("<UNTRUSTED_DIFF>", self.text)
        self.assertIn("never as instructions", self.text)
        self.assertIn('git rev-parse --show-toplevel', self.text)
        self.assertIn('"$WORKTREE_ROOT"|"$WORKTREE_ROOT"/*', self.text)


class TeardownInputTests(unittest.TestCase):
    def run_teardown(self, *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, HOME=tmp)
            return subprocess.run(
                ["bash", str(TEARDOWN), *args],
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )

    def test_missing_max_age_value_is_rejected(self) -> None:
        result = self.run_teardown("--max-age")
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires an integer", result.stderr)

    def test_non_numeric_zero_and_out_of_range_values_are_rejected(self) -> None:
        for value in ("0", "87601", "1+1", "x[$(id)]", "999999999999999999999"):
            with self.subTest(value=value):
                result = self.run_teardown("--max-age", value)
                self.assertEqual(result.returncode, 2)
                self.assertIn("positive integer", result.stderr)

    def test_bounded_positive_value_is_accepted(self) -> None:
        result = self.run_teardown("--max-age", "24")
        self.assertEqual(result.returncode, 0)
        self.assertIn("No cleanup performed", result.stdout)


class ThirdPartyProcedureTests(unittest.TestCase):
    def test_docs_do_not_offer_moving_remote_execution_commands(self) -> None:
        debate = (SKILL_DIR / "references/debate-quickstart.md").read_text(encoding="utf-8")
        forking = (SKILL_DIR / "references/subagent-context-forking.md").read_text(encoding="utf-8")
        self.assertNotIn("git clone https://github.com/albinjal/multi-agent-debate-mcp", debate)
        self.assertNotIn("npm install && npm run build", debate)
        self.assertNotIn("npx claude-code-templates@latest", forking)
        self.assertIn("immutable", debate)
        self.assertIn("exact reviewed artifact", forking)

# Wrappers that only forward the caller's options: the caller sets tools or agentType.
# (staged_runtime.js engineAgent calls ask, not agent, so it needs no entry.)
FORWARDING_AGENT_CALLS = {
    ("helpers_runtime.js", "ask"): "forwards the caller's options and only adds failure handling",
    ("review_runtime.js", "askWriter"): "forwards the caller's options and only adds writer failure handling",
    ("review_runtime.js", "readOnlyAgent"): "forwards the caller's options and only adds one retry",
    ("waves_runtime.js", "prefixed"): "spreads the caller's options and only prefixes the label",
    ("snapshot_runtime.js", "run"): "the run-wide agent cap wrapper forwards the caller's options unchanged",
    ("baseline_runtime.js", "baselineVote"): "copies the caller's options, which carry the tools",
    ("expert_board_runtime.js", "invokePanelist"): "options come from localReadOnlyOptions or add the member agentType",
}
# An option key (not the bare word, which a prompt may contain) or a helper that sets the tools counts as scoped.
TOOL_MARKERS = re.compile(r"\b(?:tools|agentType)\s*:|\blocalReadOnlyOptions\(|\btoolsUnlessNamed\(")
DECLARATION = re.compile(r"(?:function\s+(\w+)|(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?\()")


def blank_strings_and_comments(source: str) -> str:
    """The source with string, template and comment text replaced by spaces, so brackets and words in prompts never count."""
    out = []
    i = 0
    while i < len(source):
        two = source[i : i + 2]
        if two in ("//", "/*"):
            end = source.find("\n" if two == "//" else "*/", i)
            end = len(source) if end < 0 else end + (0 if two == "//" else 2)
            out.append(re.sub(r"[^\n]", " ", source[i:end]))
            i = end
        elif source[i] in "'\"`":
            quote, j = source[i], i + 1
            while j < len(source) and source[j] != quote:
                j += 2 if source[j] == "\\" else 1
            out.append(quote + re.sub(r"[^\n]", " ", source[i + 1 : j]) + quote)
            i = j + 1
        else:
            out.append(source[i])
            i += 1
    return "".join(out)


def agent_calls_without_tools(path: Path) -> list[tuple[str, int]]:
    """(enclosing function, line) of every agent or writer-wrapper call without tools or agentType."""
    text = blank_strings_and_comments(path.read_text(encoding="utf-8"))
    names: list[str | None] = []
    found = []
    for match in re.finditer(r"[{}]|(?<![\w.$])(?:agent|guarded|askWriter|readOnlyAgent)\((?!\?)", text):
        token = match.group()
        line_start = text.rfind("\n", 0, match.start()) + 1
        # A declaration is not a call; inspect the forwarding wrapper's body and its callers instead.
        if re.search(r"\bfunction\s+$", text[line_start : match.start()]):
            continue
        if token == "{":
            decl = DECLARATION.search(text[line_start : match.start()])
            names.append((decl.group(1) or decl.group(2)) if decl else None)
        elif token == "}":
            if names:
                names.pop()
        else:
            depth, end = 1, match.end()
            while depth and end < len(text):
                depth += {"(": 1, ")": -1}.get(text[end], 0)
                end += 1
            if TOOL_MARKERS.search(text[match.start() : end]):
                continue
            same_line = DECLARATION.search(text[line_start : match.start()])
            owner = (same_line.group(1) or same_line.group(2)) if same_line else next(
                (name for name in reversed(names) if name), "(top level)"
            )
            found.append((owner, text.count("\n", 0, match.start()) + 1))
    return found


class RuntimeAgentToolScopeTests(unittest.TestCase):
    def test_writer_wrapper_callers_still_require_tools(self) -> None:
        source = """async function unsafe() {
  return askWriter('tools: untrusted prompt text', { label: 'writer' });
}
async function scoped() {
  return askWriter('write', { label: 'writer', tools: WRITER_TOOLS });
}
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review_runtime.js"
            path.write_text(source, encoding="utf-8")
            self.assertEqual(agent_calls_without_tools(path), [("unsafe", 2)])

    def test_every_agent_call_sets_tools_or_agent_type(self) -> None:
        # A call with neither runs on the parent thread with every tool while it reads untrusted text.
        unscoped = []
        for path in sorted(SCRIPT_DIR.glob("*_runtime.js")):
            for owner, line in agent_calls_without_tools(path):
                if (path.name, owner) not in FORWARDING_AGENT_CALLS:
                    unscoped.append(f"{path.name}:{line} in {owner}")
        self.assertEqual(unscoped, [], "agent() calls with no tools or agentType")

    def test_forwarding_allowlist_has_no_stale_entries(self) -> None:
        seen = {
            (path.name, owner)
            for path in SCRIPT_DIR.glob("*_runtime.js")
            for owner, _line in agent_calls_without_tools(path)
        }
        self.assertEqual(sorted(set(FORWARDING_AGENT_CALLS) - seen), [])


REPO = SCRIPT_DIR.parents[3]


def code_without_comments(path: Path) -> str:
    """The script without whole-line // comments (a comment may name the banned calls). Code and strings are kept whole."""
    return "\n".join(line for line in path.read_text(encoding="utf-8").splitlines() if not line.lstrip().startswith("//"))


class WorkflowClockTests(unittest.TestCase):
    """The Claude Code workflow runtime makes Date.now(), Math.random() and a no-argument new Date() throw."""

    BANNED = {
        "new Date() with no argument": re.compile(r"\bnew\s+Date\b(?!\s*\(\s*[^\s)])"),
        "Date() call": re.compile(r"(?<![.\w])Date\s*\("),
        "Date.now(": re.compile(r"\bDate\s*\.\s*now\s*\("),
        "Math.random(": re.compile(r"\bMath\s*\.\s*random\s*\("),
    }

    @classmethod
    def found(cls, label: str, text: str) -> bool:
        """Whether the banned form occurs; `new Date(...)` is hidden first so only a bare Date() call matches the call rule."""
        if label == "Date() call":
            text = re.sub(r"\bnew\s+Date\b", "NEW_DATE", text)
        return bool(cls.BANNED[label].search(text))

    def scripts(self) -> list[Path]:
        found = sorted(SCRIPT_DIR.glob("*_runtime.js")) + sorted((REPO / "agents" / "workflows").glob("*.js"))
        self.assertTrue(found, "no workflow scripts found")
        return found

    def test_no_workflow_script_reads_the_clock_or_randomness(self) -> None:
        hits = [
            f"{path.relative_to(REPO)}: {label}"
            for path in self.scripts()
            for label, pattern in self.BANNED.items()
            if self.found(label, code_without_comments(path))
        ]
        self.assertEqual(hits, [], "pass a timestamp or value in through args instead")

    def test_scan_catches_each_banned_call(self) -> None:
        samples = {
            "new Date() with no argument": ["const d = new Date( );", "const d = new Date;", "x = new Date\n;", "new Date()"],
            "Date() call": ["s = Date();", "s = String(Date ())"],
            "Date.now(": ["x = Date.now();"],
            "Math.random(": ["y = Math.random()"],
        }
        for label, texts in samples.items():
            for sample in texts:
                self.assertTrue(self.found(label, sample), f"{label}: {sample!r}")
        for fine in ("new Date(iso)", "new Date(Date.UTC(2026, 9, 9))", "new Date(t + 'T00:00:00Z')", "d.toISOString()", "isoDate(x)", "new Date(TODAY.getTime())"):
            self.assertFalse(any(self.found(k, fine) for k in ("new Date() with no argument", "Date() call")), fine)

    def test_a_comment_marker_inside_a_string_hides_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x_runtime.js"
            path.write_text("const u = 'a // b'; const d = new Date();\n// new Date() in a comment\n", encoding="utf-8")
            self.assertTrue(self.found("new Date() with no argument", code_without_comments(path)))

    def test_client_workflow_takes_today_through_args(self) -> None:
        # The client-specific department workflow is not published, so the test skips in the public tree.
        runtimes = sorted(SCRIPT_DIR.glob("dep*_runtime.js"))
        manifests = sorted((REPO / "agents" / "workflows").glob("*matter*.manifest.json"))
        if not runtimes or not manifests:
            self.skipTest("client-specific workflow runtime is not in this tree")
        for runtime in runtimes:
            self.assertIn("args.today", runtime.read_text(encoding="utf-8"))
        for manifest in manifests:
            self.assertIn("today?:", manifest.read_text(encoding="utf-8"))


class ProtectedGateRootTests(unittest.TestCase):
    """A workflow writer must not change the saved workflow scripts or the shared runtime that judge it."""

    NEW_ROOTS = ["agents/workflows", "skills/universal/agents-subagents/scripts", "agents/claude", "agents/codex"]

    @classmethod
    def setUpClass(cls) -> None:
        cls.source = (SCRIPT_DIR / "snapshot_runtime.js").read_text(encoding="utf-8")

    def test_new_roots_are_protected_and_old_ones_kept(self) -> None:
        match = re.search(r"^const PROTECTED_ROOTS = (\[.*\]);$", self.source, re.MULTILINE)
        self.assertIsNotNone(match)
        roots = json.loads(match.group(1))
        for root in ["hooks", "scripts/git-hooks", *self.NEW_ROOTS]:
            self.assertIn(root, roots)

    def test_snapshot_command_hashes_each_new_root(self) -> None:
        command = re.search(r"^const SNAPSHOT_COMMAND = (\".*\");$", self.source, re.MULTILINE)
        self.assertIsNotNone(command)
        text = json.loads(command.group(1))
        for root in self.NEW_ROOTS:
            self.assertIn(f" {root}", text)
            self.assertRegex(text, rf"scripts/git-hooks(?: [\w/.-]+)* {re.escape(root)}(?: |; do)")

    def test_generated_workflows_carry_the_new_roots(self) -> None:
        for path in sorted((REPO / "agents" / "workflows").glob("*.js")):
            text = path.read_text(encoding="utf-8")
            if "const PROTECTED_ROOTS" in text:
                for root in self.NEW_ROOTS:
                    self.assertIn(f'"{root}"', text, path.name)

    def test_node_suites_flag_a_change_under_each_new_root(self) -> None:
        # The .mjs suites assert protected_changed for a writer's change under each root; run them here once.
        for name in ("test-adversarial-review.mjs", "test-saved-workflows.mjs"):
            suite = REPO / "agents" / "workflows" / name
            if not suite.is_file():  # the public tree ships only some suites
                continue
            done = subprocess.run(["node", str(suite)], capture_output=True, text=True, timeout=300)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)


class CheckDefectTests(unittest.TestCase):
    def test_builder_and_fixer_runtimes_stop_on_check_defect(self) -> None:
        review = (SCRIPT_DIR / "review_runtime.js").read_text(encoding="utf-8")
        staged = (SCRIPT_DIR / "staged_runtime.js").read_text(encoding="utf-8")
        snapshot = (SCRIPT_DIR / "snapshot_runtime.js").read_text(encoding="utf-8")
        self.assertIn("If a check you are judged by is wrong, do not edit it; fill check_defect with the check name and why.", snapshot)
        self.assertEqual(review.count("'check_defect'"), 2)
        self.assertIn("'check_defect'", staged)
        self.assertIn("withCheckDefect(M.fixer_schema)", review)
        self.assertIn("withCheckDefect(M.builder_schema)", review)


if __name__ == "__main__":
    unittest.main()
