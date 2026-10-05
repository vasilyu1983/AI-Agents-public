#!/usr/bin/env python3
"""Tests for generate_codex_agents.py (stdlib unittest, temp dirs only).

Each test builds its own Claude source tree, model policy, and committed Codex
tree under a temporary directory, so no test reads or writes the real catalog
except the smoke test, which only reads it.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover - Python 3.9/3.10
    tomllib = None  # type: ignore[assignment]


HERE = Path(__file__).resolve().parent
GENERATOR_PATH = HERE / "generate_codex_agents.py"

spec = importlib.util.spec_from_file_location("generate_codex_agents", GENERATOR_PATH)
assert spec and spec.loader
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)


POLICY = {
    "schema_version": 1,
    "codex": {},
    "claude": {
        "critical": {"model": "opus", "effort": "high"},
        "standard": {"model": "sonnet", "effort": "medium"},
        "mechanical": {"model": "haiku", "effort": "low"},
    },
}

TEAMMATE = (
    "**Teammate mode:** `family` is repository catalog metadata, not a Claude "
    "runtime control. Treat the launch prompt as authoritative. It must supply "
    "required skill guidance and context artifacts, owned scope and isolation, "
    "and a stopping budget; do not assume this frontmatter or the lead's "
    "conversation history is inherited."
)
LEAF = "You are a leaf worker: do not delegate or spawn subagents; return findings to the lead."
CF_LINK = "[../../skills/universal/agents-subagents/references/context-first-protocol.md](../../skills/universal/agents-subagents/references/context-first-protocol.md)"


def claude_md(
    name: str = "demo-agent",
    *,
    model: str = "opus",
    effort: str = "high",
    description: str = "Demo role. Use when testing.",
    skills: tuple[str, ...] = ("skill-one", "skill-two"),
    tools: tuple[str, ...] = ("Read", "Grep"),
    permission_mode: str | None = None,
    extra_front: str = "",
    body: str = "You review things.\n",
    leaf: bool = True,
) -> str:
    lines = ["---", f"name: {name}", "family: demo", f'description: "{description}"', "tools:"]
    lines += [f"  - {tool}" for tool in tools]
    if leaf:
        lines += ["disallowedTools:", "  - Agent"]
    if permission_mode:
        lines.append(f"permissionMode: {permission_mode}")
    lines += ["maxTurns: 10", f"model: {model}", f"effort: {effort}", "experimental:", "  cacheTtl: 1h"]
    lines.append("skills:")
    lines += [f"  - {skill}" for skill in skills]
    if extra_front:
        lines.append(extra_front)
    lines.append("---")
    head = "\n".join(lines) + "\n\n" + TEAMMATE + "\n\n"
    if leaf:
        head += LEAF + "\n\n"
    return head + body


class Tree:
    """A temporary Claude/Codex/policy layout."""

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.claude = root / "claude"
        self.codex = root / "codex"
        self.policy = root / "model-policy.json"
        self.claude.mkdir()
        self.codex.mkdir()
        self.policy.write_text(json.dumps(POLICY), encoding="utf-8")

    def close(self) -> None:
        self._tmp.cleanup()

    def add(self, text: str, name: str = "demo-agent") -> Path:
        path = self.claude / f"{name}.md"
        path.write_text(text, encoding="utf-8")
        return path

    def args(self, *extra: str) -> list[str]:
        return [
            "--claude-dir", str(self.claude),
            "--codex-dir", str(self.codex),
            "--policy", str(self.policy),
            *extra,
        ]

    def run(self, *extra: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = gen.main(self.args(*extra))
        return code, out.getvalue(), err.getvalue()

    def generate(self, name: str = "demo-agent") -> str:
        outputs = gen.generate_all(self.claude, self.policy)
        return outputs[name.replace("-", "_") + ".toml"]


class TreeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = Tree()

    def tearDown(self) -> None:
        self.tree.close()

    def instructions(self, text: str) -> str:
        return text.split('developer_instructions = """\n', 1)[1].rsplit('"""', 1)[0]


class FieldMappingTests(TreeTestCase):
    def test_header_is_exact_canonical_template(self) -> None:
        self.tree.add(claude_md())
        lines = self.tree.generate().splitlines()
        self.assertEqual(lines[0], 'name = "demo_agent"')
        self.assertEqual(lines[1], "# model_tier: critical")
        self.assertEqual(lines[2], 'description = "Demo role. Use when testing."')
        self.assertEqual(lines[3], 'sandbox_mode = "read-only"')
        self.assertEqual(lines[4], "# Linked shared skills are declared in the footer below.")
        self.assertTrue(lines[5].startswith("# Installed by deploy-preset.sh"))
        self.assertEqual(lines[6], "")
        self.assertEqual(lines[7], 'developer_instructions = """')

    def test_installer_only_fields_are_not_emitted(self) -> None:
        # deploy-preset.sh adds model pins and [[skills.config]] at install time;
        # the canonical form must carry neither.
        self.tree.add(claude_md())
        text = self.tree.generate()
        self.assertNotRegex(text, r"(?m)^model\s*=")
        self.assertNotRegex(text, r"(?m)^model_reasoning_effort\s*=")
        self.assertNotIn("[[skills.config]]\npath", text)

    def test_model_effort_pairs_map_to_policy_tiers(self) -> None:
        for model, effort, tier in (
            ("opus", "high", "critical"),
            ("sonnet", "medium", "standard"),
            ("haiku", "low", "mechanical"),
        ):
            with self.subTest(model=model):
                self.tree.add(claude_md(model=model, effort=effort))
                self.assertIn(f"# model_tier: {tier}\n", self.tree.generate())

    def test_accept_edits_maps_to_workspace_write(self) -> None:
        self.tree.add(
            claude_md(tools=("Read", "Edit", "Write"), permission_mode="acceptEdits")
        )
        self.assertIn('sandbox_mode = "workspace-write"\n', self.tree.generate())

    def test_description_quotes_are_toml_escaped(self) -> None:
        self.tree.add(claude_md(description='Say \\"hi\\" safely.'))
        self.assertIn('description = "Say \\"hi\\" safely."', self.tree.generate())

    def test_footer_lists_skills_in_source_order(self) -> None:
        self.tree.add(claude_md(skills=("zeta-skill", "alpha-skill")))
        self.assertRegex(
            self.tree.generate(),
            r"\n\n---\n\nLinked skills: zeta-skill, alpha-skill\. Declared for Codex; "
            r"deploy-preset\.sh may append per-skill `\[\[skills\.config\]\]` .+\n\"\"\"\n\Z",
        )

    @unittest.skipIf(tomllib is None, "tomllib needs Python 3.11+")
    def test_output_is_valid_toml_even_with_quotes_and_backslashes(self) -> None:
        body = 'Use a path like C:\\temp and a literal """ fence.\n'
        self.tree.add(claude_md(body=body))
        parsed = tomllib.loads(self.tree.generate())
        self.assertEqual(parsed["name"], "demo_agent")
        self.assertIn('C:\\temp and a literal """ fence.', parsed["developer_instructions"])


class DeterministicRewriteTests(TreeTestCase):
    def test_teammate_paragraph_becomes_launch_prompt_authority(self) -> None:
        self.tree.add(claude_md())
        body = self.instructions(self.tree.generate())
        self.assertTrue(body.startswith("**Launch-prompt authority:** "))
        self.assertNotIn("Teammate mode", body)

    def test_leaf_line_becomes_codex_delegation_boundary(self) -> None:
        self.tree.add(claude_md())
        paragraphs = self.instructions(self.tree.generate()).split("\n\n")
        self.assertEqual(
            paragraphs[1],
            "Do not delegate or spawn subagents. Return your result to the parent agent.",
        )
        self.assertNotIn(LEAF, self.tree.generate())
        self.assertEqual(paragraphs[2], "You review things.")

    def test_non_leaf_gets_no_delegation_line(self) -> None:
        self.tree.add(claude_md(leaf=False))
        self.assertNotIn("Do not delegate", self.tree.generate())

    def test_context_first_links_become_inline_gloss(self) -> None:
        body = (
            f"1. Read in order. See {CF_LINK}. Do not rediscover.\n"
            f"- Start from context. Follow {CF_LINK}; ask for missing context.\n"
        )
        self.tree.add(claude_md(body=body))
        text = self.tree.generate()
        self.assertNotIn("context-first-protocol.md", text)
        self.assertIn(
            "1. Read in order. (context-first rule: consume prepared artifacts in the order "
            "listed above; never re-derive what an artifact already answers; record gaps in "
            "Context Used). Do not rediscover.",
            text,
        )
        self.assertIn("- Start from context. (context-first rule: ", text)

    def test_other_reference_links_stay_for_the_installer(self) -> None:
        link = "[../../skills/universal/agents-subagents/references/shared-context-pattern.md](../../skills/universal/agents-subagents/references/shared-context-pattern.md)"
        self.tree.add(claude_md(body=f"Follow {link}.\n"))
        self.assertIn(f"Follow {link}.", self.tree.generate())

    def test_member_ids_become_snake_case_but_skills_and_prefixes_do_not(self) -> None:
        self.tree.add(claude_md(name="other-agent"), name="other-agent")
        body = (
            "Route to `other-agent` or other-agent.\n"
            "Not other-agent-extra, not pre-other-agent, not skill-one.\n"
        )
        self.tree.add(claude_md(body=body))
        text = self.tree.generate()
        self.assertIn("Route to `other_agent` or other_agent.", text)
        self.assertIn("Not other-agent-extra, not pre-other-agent, not skill-one.", text)
        self.assertIn("Linked skills: skill-one, skill-two.", text)

    def test_trailing_additional_skill_scope_moves_after_footer(self) -> None:
        body = "Main body.\n\n## Additional Skill Scope\n\nUse skill-two for X.\n"
        self.tree.add(claude_md(body=body))
        text = self.tree.generate()
        self.assertTrue(
            text.endswith(
                "standard-tier agents inherit configured Codex defaults.\n\n"
                "## Additional Skill Scope\n\nUse skill-two for X.\n\"\"\"\n"
            ),
            text[-300:],
        )
        self.assertIn("Main body.\n\n---\n\nLinked skills:", text)

    def test_legacy_teammate_note_is_dropped_and_separator_merged(self) -> None:
        body = "Main body.\n\n---\n\nTeammate note: For deeper analysis, consult skills.\n\n\n"
        self.tree.add(claude_md(body=body))
        text = self.tree.generate()
        self.assertNotIn("Teammate note", text)
        self.assertIn("Main body.\n\n---\n\nLinked skills:", text)
        self.assertEqual(text.count("\n---\n"), 1)


class MarkerTests(TreeTestCase):
    def test_claude_only_block_is_removed_with_its_blank_line(self) -> None:
        body = (
            "Intro.\n\n<!-- claude-only -->\nUse Bash only for inspection.\n"
            "<!-- /claude-only -->\n\nNext paragraph.\n"
        )
        self.tree.add(claude_md(body=body))
        text = self.tree.generate()
        self.assertNotIn("Use Bash", text)
        self.assertNotIn("claude-only", text)
        self.assertIn("Intro.\n\nNext paragraph.\n", text)

    def test_codex_only_block_is_emitted_only_for_codex(self) -> None:
        body = (
            "1. Step one.\n<!-- claude-only -->\n2. When in doubt, ask.\n<!-- /claude-only -->\n"
            "<!-- codex-only\n2. State the ambiguity and stop.\n-->\n3. Step three.\n"
        )
        self.tree.add(claude_md(body=body))
        text = self.tree.generate()
        self.assertIn("1. Step one.\n2. State the ambiguity and stop.\n3. Step three.\n", text)
        self.assertNotIn("When in doubt", text)
        self.assertNotIn("codex-only", text)

    def test_single_line_codex_only_form(self) -> None:
        body = "A.\n<!-- codex-only: B for Codex. -->\nC.\n"
        self.tree.add(claude_md(body=body))
        self.assertIn("A.\nB for Codex.\nC.\n", self.tree.generate())

    def test_codex_text_is_inside_an_html_comment_in_the_claude_file(self) -> None:
        # The constraint: Claude reads the .md directly, so Codex-only text must
        # sit inside a comment. Every codex-only opener must be closed by -->.
        body = "<!-- codex-only\nCodex text.\n-->\n"
        source = claude_md(body=body)
        start = source.index("<!-- codex-only")
        self.assertLess(source.index("Codex text."), source.index("-->", start))

    def test_unbalanced_markers_fail_closed(self) -> None:
        for body in (
            "<!-- claude-only -->\nNever closed.\n",
            "Text.\n<!-- /claude-only -->\n",
            "<!-- codex-only\nNever closed.\n",
            "<!-- claude-only -->\n<!-- claude-only -->\nX\n<!-- /claude-only -->\n",
            "<!-- codex-only: ok -->\n<!-- codex-replace -->\n",
        ):
            with self.subTest(body=body):
                self.tree.add(claude_md(body=body))
                code, _out, err = self.tree.run()
                self.assertEqual(code, 2)
                self.assertIn("demo-agent.md", err)
                self.assertEqual(len(err.strip().splitlines()), 1)


class FailClosedTests(TreeTestCase):
    def assert_input_error(self, text: str, fragment: str) -> None:
        self.tree.add(text)
        code, out, err = self.tree.run()
        self.assertEqual(code, 2, out + err)
        self.assertEqual(len(err.strip().splitlines()), 1, err)
        self.assertIn("demo-agent.md", err)
        self.assertIn(fragment, err)

    def test_missing_front_matter(self) -> None:
        self.assert_input_error("No front matter here.\n", "front matter")

    def test_unterminated_front_matter(self) -> None:
        self.assert_input_error("---\nname: demo-agent\n", "front matter")

    def test_unknown_model_value(self) -> None:
        self.assert_input_error(claude_md(model="no-such-model"), "no-such-model")

    def test_effort_not_matching_policy(self) -> None:
        self.assert_input_error(claude_md(model="opus", effort="low"), "opus/low")

    def test_name_must_match_file_stem(self) -> None:
        self.assert_input_error(claude_md(name="other-name"), "other-name")

    def test_unknown_front_matter_key(self) -> None:
        self.assert_input_error(claude_md(extra_front="hooks: something"), "hooks")

    def test_unknown_permission_mode(self) -> None:
        self.assert_input_error(claude_md(permission_mode="bypassPermissions"), "bypassPermissions")

    def test_permission_mode_must_agree_with_edit_tools(self) -> None:
        self.assert_input_error(claude_md(permission_mode="acceptEdits"), "acceptEdits")

    def test_missing_teammate_paragraph(self) -> None:
        text = claude_md().replace(TEAMMATE, "Some other opening.")
        self.assert_input_error(text, "Teammate mode")

    def test_missing_skills(self) -> None:
        self.assert_input_error(claude_md(skills=()), "skills")

    def test_explicit_empty_skills_is_accepted(self) -> None:
        # The public build withholds some skills, leaving members with `skills: []`;
        # only that explicit form passes, an empty block above still fails closed.
        self.tree.add(claude_md(skills=()).replace("skills:\n", "skills: []\n"))
        self.assertIn("Linked skills: none.", self.tree.generate())

    def test_bad_policy_file(self) -> None:
        self.tree.add(claude_md())
        self.tree.policy.write_text("{not json", encoding="utf-8")
        code, _out, err = self.tree.run()
        self.assertEqual(code, 2)
        self.assertIn("model-policy.json", err)


class CliTests(TreeTestCase):
    def test_check_passes_after_write(self) -> None:
        self.tree.add(claude_md())
        code, _out, _err = self.tree.run("--write")
        self.assertEqual(code, 0)
        self.assertTrue((self.tree.codex / "demo_agent.toml").exists())
        code, out, _err = self.tree.run("--check")
        self.assertEqual(code, 0, out)

    def test_check_fails_and_names_drifted_agent(self) -> None:
        self.tree.add(claude_md())
        self.tree.run("--write")
        target = self.tree.codex / "demo_agent.toml"
        target.write_text(target.read_text(encoding="utf-8") + "# drift\n", encoding="utf-8")
        code, out, _err = self.tree.run("--check")
        self.assertEqual(code, 1)
        self.assertIn("demo-agent", out)

    def test_check_fails_on_missing_and_orphan_files(self) -> None:
        self.tree.add(claude_md())
        code, out, _err = self.tree.run("--check")
        self.assertEqual(code, 1)
        self.assertIn("demo-agent", out)
        self.tree.run("--write")
        (self.tree.codex / "ghost_agent.toml").write_text('name = "ghost_agent"\n', encoding="utf-8")
        code, out, _err = self.tree.run("--check")
        self.assertEqual(code, 1)
        self.assertIn("ghost_agent.toml", out)

    def test_default_mode_reports_without_writing(self) -> None:
        self.tree.add(claude_md())
        code, out, _err = self.tree.run()
        self.assertEqual(code, 0)
        self.assertIn("would create: 1", out)
        self.assertFalse((self.tree.codex / "demo_agent.toml").exists())

    def test_diff_mode_shows_unified_diff_for_one_agent(self) -> None:
        self.tree.add(claude_md())
        self.tree.run("--write")
        target = self.tree.codex / "demo_agent.toml"
        target.write_text(
            target.read_text(encoding="utf-8").replace("You review things.", "Old text."),
            encoding="utf-8",
        )
        for name in ("demo-agent", "demo_agent"):
            with self.subTest(name=name):
                code, out, _err = self.tree.run("--diff", name)
                self.assertEqual(code, 0)
                self.assertIn("-Old text.", out)
                self.assertIn("+You review things.", out)

    def test_diff_unknown_agent_fails_closed(self) -> None:
        self.tree.add(claude_md())
        code, _out, err = self.tree.run("--diff", "nobody")
        self.assertEqual(code, 2)
        self.assertIn("nobody", err)


class ShippedCatalogSmokeTest(unittest.TestCase):
    """Run the shipped default inputs with no overrides (read-only)."""

    def test_real_catalog_generates_one_toml_per_claude_member(self) -> None:
        claude_dir = gen.DEFAULT_CLAUDE_DIR
        sources = sorted(p for p in claude_dir.glob("*.md") if p.name != "README.md")
        outputs = gen.generate_all(claude_dir, gen.DEFAULT_POLICY)
        self.assertEqual(len(outputs), len(sources))
        for text in outputs.values():
            self.assertIn("**Launch-prompt authority:**", text)
            self.assertRegex(text, r"(?m)^Linked skills: [^.\n]+\. Declared for Codex; ")
            if tomllib is not None:
                tomllib.loads(text)

    def test_generate_member_matches_generate_all(self) -> None:
        claude_dir = gen.DEFAULT_CLAUDE_DIR
        outputs = gen.generate_all(claude_dir, gen.DEFAULT_POLICY)
        source = claude_dir / "qa-test-reviewer.md"
        self.assertEqual(gen.generate_member(source), outputs["qa_test_reviewer.toml"])


class InstallerFallbackTest(unittest.TestCase):
    """deploy-preset.sh must convert a missing Codex member through this generator only."""

    def test_fallback_calls_generate_member(self) -> None:
        body = (HERE / "deploy-preset.sh").read_text(encoding="utf-8")
        start = body.index("generate_codex_from_claude() {")
        function = body[start:body.index("member_source_for_install() {")]
        self.assertIn("gen.generate_member(", function)
        # The retired hand-rolled converter derived sandbox_mode from tools itself.
        self.assertNotIn("sandbox_mode =", function)
        self.assertIn('generate_codex_from_claude "$member_id" || return 1', body)


if __name__ == "__main__":
    unittest.main()
