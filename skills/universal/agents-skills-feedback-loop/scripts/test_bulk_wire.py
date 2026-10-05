"""Regression coverage for the manual/automatic wiring contract."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location("bulk_wire", Path(__file__).with_name("bulk_wire.py"))
wire = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wire)


class WiringTests(unittest.TestCase):
    def test_generated_seed_matches_manual_template(self):
        template = Path(__file__).resolve().parents[1] / "assets/learnings.template.md"
        self.assertEqual(wire.consolidated_template("sample"), template.read_text().replace("<SKILL_NAME>", "sample"))

    def test_wiring_preserves_existing_learning_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = Path(temp) / "sample"
            skill.mkdir()
            (skill / "SKILL.md").write_text("# Sample\n\n## See Also\nExisting navigation.\n")
            learning = skill / "learnings.consolidated.md"
            learning.write_text("Existing reviewed lesson.\n")
            self.assertEqual(wire.is_eligible(skill), (True, "eligible"))
            wire.wire(skill, dry_run=True)
            self.assertNotIn("## Learnings Loop", (skill / "SKILL.md").read_text())
            wire.wire(skill, dry_run=False)
            self.assertEqual(learning.read_text(), "Existing reviewed lesson.\n")
            self.assertEqual(wire.is_eligible(skill), (False, "already wired"))
            body = (skill / "SKILL.md").read_text()
            self.assertLess(body.index("## Learnings Loop"), body.index("## See Also"))
            self.assertIn("Otherwise skip both", body)


if __name__ == "__main__":
    unittest.main()
