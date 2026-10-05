#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
try:
    import tomllib
except ImportError:  # Python 3.10 and older
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError as exc:  # pragma: no cover - environment guard
        raise SystemExit(
            "TOML support unavailable: run with Python 3.11+ (this file needs "
            "the stdlib tomllib) or install the 'tomli' backport."
        ) from exc
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VALIDATOR_PATH = HERE / "validate_catalog_integrity.py"
DEPLOY = HERE / "deploy-preset.sh"
POLICY_PATH = ROOT / "data/model-policy.json"

spec = importlib.util.spec_from_file_location("catalog_integrity", VALIDATOR_PATH)
assert spec and spec.loader
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ModelPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    def test_current_policy_is_valid(self) -> None:
        self.assertEqual(validator.validate_model_policy(self.policy), [])

    def test_rejects_missing_tier_and_toml_injection(self) -> None:
        policy = deepcopy(self.policy)
        del policy["codex"]["mechanical"]
        policy["codex"]["critical"]["model"] = 'safe"\n[mcp_servers.bad]'
        complaints = validator.validate_model_policy(policy)
        self.assertTrue(any("tiers must be exactly" in item for item in complaints))
        self.assertTrue(any("unsafe model" in item for item in complaints))

    def test_rejects_invalid_global_claude_override_policy(self) -> None:
        policy = deepcopy(self.policy)
        policy["claude_global_subagent_override"]["unexpected"] = True
        policy["claude_global_subagent_override"]["allowed_models"] = [
            "claude-opus-5",
            "claude-opus-5",
            'unsafe"\n[agents.bad]',
        ]
        policy["unexpected_root"] = True
        complaints = validator.validate_model_policy(policy)
        self.assertTrue(any("unknown keys: unexpected_root" in item for item in complaints))
        self.assertTrue(any("global_subagent_override has unknown keys" in item for item in complaints))
        self.assertTrue(any("allowed_models must contain unique safe model IDs" in item for item in complaints))

    def test_rejects_missing_or_non_list_global_claude_override_policy(self) -> None:
        policy = deepcopy(self.policy)
        del policy["claude_global_subagent_override"]
        complaints = validator.validate_model_policy(policy)
        self.assertTrue(any("missing keys: claude_global_subagent_override" in item for item in complaints))

        policy = deepcopy(self.policy)
        policy["claude_global_subagent_override"]["allowed_models"] = "claude-opus-5"
        complaints = validator.validate_model_policy(policy)
        self.assertTrue(any("allowed_models must be a non-empty list" in item for item in complaints))

    def test_rejects_unknown_or_missing_claude_model_effort_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_members = root / "codex"
            claude_members = root / "claude"
            codex_members.mkdir()
            claude_members.mkdir()
            (codex_members / "unknown_model.toml").write_text(
                '# model_tier: critical\ndescription = "fixture"\n', encoding="utf-8"
            )
            (claude_members / "unknown-model.md").write_text(
                "---\nmodel: claude-not-in-policy\neffort: high\n---\n",
                encoding="utf-8",
            )
            (codex_members / "missing_effort.toml").write_text(
                '# model_tier: standard\ndescription = "fixture"\n', encoding="utf-8"
            )
            (claude_members / "missing-effort.md").write_text(
                "---\nmodel: claude-sonnet-4-6\n---\n", encoding="utf-8"
            )
            summary: dict[str, object] = {}
            errors: list[str] = []
            with (
                mock.patch.object(validator, "CODEX_MEMBERS", codex_members),
                mock.patch.object(validator, "CLAUDE_MEMBERS", claude_members),
            ):
                validator.check_codex_model_pins(summary, errors, self.policy)

        parity = summary["cross_runtime_model_tier_parity"]
        self.assertTrue(any("unknown-model: unknown Claude model/effort" in item for item in parity))
        self.assertTrue(any("missing-effort: unknown Claude model/effort" in item for item in parity))
        self.assertTrue(any("Claude/Codex model tier drift" in item for item in errors))

    def test_materializes_all_three_tiers_and_parses_toml(self) -> None:
        cases = {
            "ai-agent-architect": (
                self.policy["codex"]["critical"]["model"],
                self.policy["codex"]["critical"]["model_reasoning_effort"],
            ),
            "data-instrumentation-analyst": (
                self.policy["codex"]["mechanical"]["model"],
                self.policy["codex"]["mechanical"]["model_reasoning_effort"],
            ),
            "product-manager": (None, None),
        }
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            for member in cases:
                result = subprocess.run(
                    ["bash", str(DEPLOY), member, "--member", "--platform", "codex", "--project"],
                    cwd=target,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for member, expected in cases.items():
                path = target / ".codex/agents" / f"{member.replace('-', '_')}.toml"
                data = tomllib.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(data.get("model"), expected[0])
                self.assertEqual(data.get("model_reasoning_effort"), expected[1])

    def test_rejects_path_traversal_before_removal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["bash", str(DEPLOY), "../config", "--member", "--platform", "codex",
                 "--project", "--remove", "--force"],
                cwd=tmp,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsafe member id", result.stderr)

    def test_rejects_symlinked_managed_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scope = root / "scope"
            outside = root / "outside"
            scope.mkdir()
            outside.mkdir()
            (scope / ".codex").symlink_to(outside, target_is_directory=True)
            result = subprocess.run(
                ["bash", str(DEPLOY), "product-manager", "--member", "--platform", "codex", "--project"],
                cwd=scope,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsafe managed base contains symlink", result.stderr)

    def test_accepts_repo_path_through_filesystem_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scope = root / "scope"
            alias = root / "alias"
            scope.mkdir()
            alias.symlink_to(scope, target_is_directory=True)
            result = subprocess.run(
                ["bash", str(DEPLOY), "product-manager", "--member", "--platform", "codex",
                 "--repo", str(alias)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((scope / ".codex/agents/product_manager.toml").is_file())

    def test_rejects_symlinked_managed_base_through_filesystem_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scope = root / "scope"
            alias = root / "alias"
            outside = root / "outside"
            scope.mkdir()
            outside.mkdir()
            alias.symlink_to(scope, target_is_directory=True)
            (scope / ".codex").symlink_to(outside, target_is_directory=True)
            result = subprocess.run(
                ["bash", str(DEPLOY), "product-manager", "--member", "--platform", "codex",
                 "--repo", str(alias)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsafe managed base contains symlink", result.stderr)


if __name__ == "__main__":
    unittest.main()
