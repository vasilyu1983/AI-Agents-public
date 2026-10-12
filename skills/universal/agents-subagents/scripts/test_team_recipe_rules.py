#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "catalog_integrity", HERE / "validate_catalog_integrity.py"
)
assert spec and spec.loader
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

GOOD = {
    "debate": {"method": "pre-mortem", "decision_masks": ["inversion", "second-order"]},
    "budget": {"max_rounds": 2, "max_turns_per_member": 10, "token_envelope": 100000},
    "verification": {"mode": "heterogeneous", "rule": "parent thread checks"},
    "owned_files": ["a: src/**", "b: docs/**"],
}


def methods_dir(tmp: str) -> Path:
    path = Path(tmp)
    (path / "pre-mortem.md").write_text("# m\n", encoding="utf-8")
    return path


class TeamRecipeRuleTests(unittest.TestCase):
    def problems(self, **changes: object) -> list[str]:
        data = {**GOOD, **changes}
        with tempfile.TemporaryDirectory() as tmp:
            return validator.team_recipe_problems("t", data, methods_dir(tmp))

    def test_good_recipe_passes(self) -> None:
        self.assertEqual(self.problems(), [])

    def test_three_masks_fail(self) -> None:
        masks = ["inversion", "second-order", "base-rate-mask"]
        found = self.problems(debate={"method": "pre-mortem", "decision_masks": masks})
        self.assertEqual(len(found), 1)
        self.assertIn("3 decision_masks", found[0])

    def test_unknown_method_fails(self) -> None:
        found = self.problems(debate={"method": "no-such-method", "decision_masks": []})
        self.assertIn("not a file in debate-methods", found[0])

    def test_missing_budget_and_verification_fail(self) -> None:
        data = {k: v for k, v in GOOD.items() if k not in ("budget", "verification")}
        with tempfile.TemporaryDirectory() as tmp:
            found = validator.team_recipe_problems("t", data, methods_dir(tmp))
        self.assertTrue(any("missing budget" in p for p in found))
        self.assertTrue(any("missing verification" in p for p in found))

    def test_incomplete_budget_fails(self) -> None:
        found = self.problems(budget={"max_rounds": 2})
        self.assertEqual(len(found), 2)

    def test_overlap_without_exclusion_fails(self) -> None:
        found = self.problems(owned_files=["a: docs/**, README.md", "b: docs/prd/**"])
        self.assertIn("ownership overlap", found[0])

    def test_single_star_glob_overlap_fails(self) -> None:
        found = self.problems(owned_files=["a: docs/*.md", "b: docs/guide.md"])
        self.assertIn("ownership overlap", found[0])

    def test_self_verification_fails(self) -> None:
        found = self.problems(verification={"mode": "Self", "rule": "producer checks"})
        self.assertEqual(len(found), 1)
        self.assertIn("'self'", found[0])

    def test_overlap_with_exclusion_passes(self) -> None:
        owned = ["a: docs/**, README.md (excluding docs/prd/**)", "b: docs/prd/**"]
        self.assertEqual(self.problems(owned_files=owned), [])

    def test_exclusion_with_possible_overlap_is_not_containment(self) -> None:
        for exclusion, other in [
            ("docs/*.md", "docs/sub/**"),
            ("docs/report-*.md", "docs/report-data/**"),
        ]:
            with self.subTest(exclusion=exclusion):
                owned = [f"a: docs/** (excluding {exclusion})", f"b: {other}"]
                self.assertTrue(any("ownership overlap" in p for p in self.problems(owned_files=owned)))

    def test_identical_glob_exclusion_passes(self) -> None:
        owned = ["a: docs/** (excluding docs/*.md)", "b: docs/*.md"]
        self.assertEqual(self.problems(owned_files=owned), [])

    def test_literal_subtree_exclusion_passes(self) -> None:
        owned = ["a: docs/** (excluding docs/prd/**)", "b: docs/prd/nested/*.md"]
        self.assertEqual(self.problems(owned_files=owned), [])

    def test_read_only_and_disjoint_entries_ignored(self) -> None:
        owned = ["a: src/**", "b, c: read-only", "d: src2/**", "none - read-only analysis team"]
        self.assertEqual(self.problems(owned_files=owned), [])

    def test_shipped_recipes_pass(self) -> None:
        summary: dict[str, object] = {}
        errors: list[str] = []
        validator.check_team_recipe_rules(summary, errors)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
