#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
AUDIT = HERE / "audit-effective-runtime.py"
POLICY = json.loads((ROOT / "data/model-policy.json").read_text(encoding="utf-8"))


class EffectiveRuntimeAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.codex_agents = self.root / "codex-agents"
        self.claude_agents = self.root / "claude-agents"
        self.codex_agents.mkdir()
        self.claude_agents.mkdir()
        standard = POLICY["codex"]["standard"]
        self.codex_config = self.root / "config.toml"
        self.codex_config.write_text(
            "[agents]\n"
            f'default_subagent_model = "{standard["model"]}"\n'
            f'default_subagent_reasoning_effort = "{standard["model_reasoning_effort"]}"\n',
            encoding="utf-8",
        )
        self.claude_settings = self.root / "settings.json"
        self.claude_settings.write_text("{}\n", encoding="utf-8")
        self.policy_path = self.root / "policy.json"
        self.policy_path.write_text(json.dumps(POLICY), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_audit(self, *extra: str, env_override: str | None = None) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        env.pop("CLAUDE_CODE_SUBAGENT_MODEL", None)
        if env_override is not None:
            env["CLAUDE_CODE_SUBAGENT_MODEL"] = env_override
        return subprocess.run(
            [
                sys.executable, str(AUDIT),
                "--policy", str(self.policy_path),
                "--codex-config", str(self.codex_config),
                "--codex-agents", str(self.codex_agents),
                "--claude-settings", str(self.claude_settings),
                "--claude-agents", str(self.claude_agents),
                *extra,
            ],
            text=True,
            capture_output=True,
            check=False,
            env=env,
            timeout=3,
        )

    def test_recognizes_effective_standard_tier(self) -> None:
        (self.codex_agents / "product_manager.toml").write_text(
            'name = "product_manager"\ndescription = "fixture"\n'
            'developer_instructions = "fixture"\n', encoding="utf-8"
        )
        standard = POLICY["claude"]["standard"]
        (self.claude_agents / "product-manager.md").write_text(
            f'---\nname: product-manager\nmodel: {standard["model"]}\n'
            f'effort: {standard["effort"]}\n---\nfixture\n', encoding="utf-8"
        )
        result = self.run_audit("--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["codex"]["tiers"], {"standard": 1})
        self.assertEqual(report["claude"]["tiers"], {"standard": 1})

    def test_reports_codex_default_drift(self) -> None:
        self.codex_config.write_text(
            '[agents]\ndefault_subagent_model = "different-model"\n'
            'default_subagent_reasoning_effort = "medium"\n', encoding="utf-8"
        )
        result = self.run_audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn("inherited standard tier differs", result.stderr)

    def test_missing_agents_table_reports_provisioning_instruction(self) -> None:
        # A clean Codex install has no [agents] table. The audit must say how to get
        # one -- a bare "missing an [agents] table" FAIL is unactionable, and the
        # operator needs to know subagents still run (agents.enabled defaults true).
        self.codex_config.write_text('model = "unrelated"\n', encoding="utf-8")
        result = self.run_audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing an [agents] table", result.stderr)
        self.assertIn("deploy-preset.sh", result.stderr)
        self.assertIn("default_subagent_model", result.stderr)
        self.assertIn("default_subagent_reasoning_effort", result.stderr)
        self.assertIn("agents.enabled defaults to true", result.stderr)

    def test_requires_materialized_pins_for_critical_agent(self) -> None:
        (self.codex_agents / "ai_evals_observer.toml").write_text(
            'name = "ai_evals_observer"\ndescription = "fixture"\n'
            'developer_instructions = "fixture"\n', encoding="utf-8"
        )
        result = self.run_audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn("must materialize tier critical", result.stderr)

    def test_rejects_unknown_policy_and_runtime_config_keys(self) -> None:
        bad = json.loads(json.dumps(POLICY))
        bad["codex"]["standard"]["mystery"] = True
        self.policy_path.write_text(json.dumps(bad), encoding="utf-8")
        result = self.run_audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown keys: mystery", result.stderr)

        self.policy_path.write_text(json.dumps(POLICY), encoding="utf-8")
        with self.codex_config.open("a", encoding="utf-8") as handle:
            handle.write('mystery_runtime_key = "ignored-by-runtime"\n')
        result = self.run_audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Codex [agents] has unknown keys: mystery_runtime_key", result.stderr)

    def test_rejects_invalid_global_override_policy_schema(self) -> None:
        bad = json.loads(json.dumps(POLICY))
        bad["claude_global_subagent_override"]["allowed_models"] = ["claude-opus-5", "claude-opus-5"]
        bad["claude_global_subagent_override"]["mystery"] = True
        self.policy_path.write_text(json.dumps(bad), encoding="utf-8")
        result = self.run_audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn("global_subagent_override has unknown keys: mystery", result.stderr)
        self.assertIn("allowed_models must contain unique safe model IDs", result.stderr)

    def test_explicit_allowed_override_passes_without_exposing_value(self) -> None:
        allowed = POLICY["claude_global_subagent_override"]["allowed_models"][0]
        self.claude_settings.write_text(
            json.dumps({"env": {"CLAUDE_CODE_SUBAGENT_MODEL": allowed}}), encoding="utf-8"
        )
        result = self.run_audit("--json", env_override=allowed)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(
            report["claude"]["global_override_sources"],
            ["current-process environment", "persistent Claude settings"],
        )
        self.assertEqual(report["claude"]["global_override_policy"], "allowed")
        self.assertNotIn(allowed, result.stdout + result.stderr)

    def test_shipped_policy_accepts_operator_sonnet_choice(self) -> None:
        # Commit 27bb2e585 preserves this deliberate host preference. The audit
        # must agree with setup without accepting arbitrary global overrides.
        selected = "claude-sonnet-5-5"
        self.claude_settings.write_text(
            json.dumps({"env": {"CLAUDE_CODE_SUBAGENT_MODEL": selected}}), encoding="utf-8"
        )
        result = self.run_audit(
            "--policy", str(ROOT / "data/model-policy.json"), "--json", env_override=selected,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["claude"]["global_override_policy"], "allowed")
        self.assertEqual(
            report["claude"]["global_override_sources"],
            ["current-process environment", "persistent Claude settings"],
        )
        self.assertNotIn(selected, result.stdout + result.stderr)

    def test_allowed_sonnet_override_does_not_hide_wrong_critical_tier(self) -> None:
        (self.claude_agents / "ai-evals-observer.md").write_text(
            '---\nname: ai-evals-observer\nmodel: sonnet\neffort: low\n---\nfixture\n',
            encoding="utf-8",
        )
        result = self.run_audit(
            "--policy", str(ROOT / "data/model-policy.json"), "--json",
            env_override="claude-sonnet-5-5",
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["claude"]["global_override_policy"], "allowed")
        self.assertIn("ai-evals-observer", result.stdout)

    def test_rejects_unapproved_override_without_exposing_value(self) -> None:
        secretish = "do-not-print-this-value"
        self.claude_settings.write_text(
            json.dumps({"env": {"CLAUDE_CODE_SUBAGENT_MODEL": secretish}}), encoding="utf-8"
        )
        result = self.run_audit(env_override=secretish)
        self.assertEqual(result.returncode, 1)
        self.assertIn("current-process environment, persistent Claude settings", result.stderr)
        self.assertIn("value withheld", result.stderr)
        self.assertNotIn(secretish, result.stdout + result.stderr)

    def test_rejects_mixed_allowed_and_unapproved_override_sources(self) -> None:
        allowed = POLICY["claude_global_subagent_override"]["allowed_models"][0]
        self.claude_settings.write_text(
            json.dumps({"env": {"CLAUDE_CODE_SUBAGENT_MODEL": allowed}}), encoding="utf-8"
        )
        result = self.run_audit(env_override="not-approved")
        self.assertEqual(result.returncode, 1)
        self.assertIn("current-process environment", result.stderr)
        self.assertNotIn("persistent Claude settings", result.stderr)
        self.assertNotIn("not-approved", result.stdout + result.stderr)

    def test_rejects_non_object_settings_without_traceback(self) -> None:
        self.claude_settings.write_text("[]\n", encoding="utf-8")
        result = self.run_audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn("persistent settings could not be parsed", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_special_agent_file_fails_without_blocking(self) -> None:
        os.mkfifo(self.codex_agents / "product_manager.toml")
        result = self.run_audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot be parsed", result.stderr)

    def test_exact_regular_symlink_remains_a_supported_install_shape(self) -> None:
        source = self.root / "product_manager.toml"
        source.write_text(
            'name = "product_manager"\ndescription = "fixture"\n'
            'developer_instructions = "fixture"\n', encoding="utf-8",
        )
        (self.codex_agents / "product_manager.toml").symlink_to(source)
        result = self.run_audit()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unknown_inventory_requires_explicit_exemption(self) -> None:
        (self.codex_agents / "personal_helper.toml").write_text(
            'name = "personal_helper"\ndescription = "fixture"\n'
            'developer_instructions = "fixture"\n', encoding="utf-8"
        )
        result = self.run_audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn("require an explicit exemption", result.stderr)
        result = self.run_audit("--exempt-codex", "personal-helper", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["codex"]["exempt"], ["personal-helper"])

    def test_opt_in_only_members_are_optional_under_complete_gate(self) -> None:
        teams = self.root / "teams"
        (teams / "optional-team").mkdir(parents=True)
        (teams / "optional-team" / "team.yaml").write_text(
            "name: optional-team\nmembers:\n- marketing-strategist\n"
            "- software-ios-specialist\ninstall: opt-in\n", encoding="utf-8"
        )
        (teams / "default-team").mkdir()
        (teams / "default-team" / "team.yaml").write_text(
            "name: default-team\nmembers:\n- software-ios-specialist\n", encoding="utf-8"
        )
        result = self.run_audit("--require-complete", "--teams-dir", str(teams), "--json")
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        for platform in ("codex", "claude"):
            self.assertIn("marketing-strategist", report[platform]["optional_not_installed"])
            self.assertNotIn("marketing-strategist", report[platform]["missing"])
            # listed by a default team too -> still required
            self.assertIn("software-ios-specialist", report[platform]["missing"])

    def test_complete_inventory_is_an_explicit_gate(self) -> None:
        result = self.run_audit("--require-complete")
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing canonical Codex agents", result.stderr)
        self.assertIn("missing canonical Claude agents", result.stderr)


if __name__ == "__main__":
    unittest.main()
