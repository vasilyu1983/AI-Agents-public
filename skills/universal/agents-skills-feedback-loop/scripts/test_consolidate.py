"""Reject malformed learning records before reporting success or proposals."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(os.environ.get("FEEDBACK_TEST_SCRIPTS", Path(__file__).parent))

MALFORMED_RECORDS = [
    "- undated learning",
    "- [2026-02-30] impossible date",
    "- [2026-09-28] ",
    "- [2026-09-28] first line\ncontinued entry",
    "## Invented Section\n- [2026-09-28] misplaced entry",
    "<!-- unterminated template comment\n- [2026-09-28] hidden entry",
    "<!-- comment --> - [2026-09-28] hidden entry",
    "<!-- multiline\ncomment --> - [2026-09-28] hidden entry",
]


class ConsolidateTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp_path = Path(self._tmp.name)

    def test_malformed_records_fail_closed(self):
        for mode in ("--audit", "--dry-run"):
            for record in MALFORMED_RECORDS:
                with self.subTest(mode=mode, record=record), tempfile.TemporaryDirectory() as tmp:
                    tmp_path = Path(tmp)
                    (tmp_path / "SKILL.md").write_text("## Learnings Loop\n")
                    raw = tmp_path / "learnings.md"
                    raw.write_text("# Learnings\n\n## Domain Knowledge\n" + record + "\n")
                    before = raw.read_bytes()
                    result = subprocess.run([sys.executable, str(SCRIPTS / "consolidate.py"),
                                             str(tmp_path), mode], capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn("status=ok", result.stdout)
                    self.assertNotIn("PROMOTE", result.stdout)
                    self.assertEqual(raw.read_bytes(), before)

    def test_invalid_append_date_does_not_create_raw_file(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "append_learning.py"),
                                 str(self.tmp_path), "--section", "Domain Knowledge",
                                 "--text", "Synthetic lesson", "--date", "2026-02-30"],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.tmp_path / "learnings.md").exists())

    def test_valid_records_and_filter_override_pass(self):
        (self.tmp_path / "SKILL.md").write_text("## Learnings Loop\n")
        (self.tmp_path / "learnings.md").write_text(
            "# Learnings\n\n## Domain Knowledge\n<!-- template placeholder -->\n"
            "<!-- multiline\nplaceholder -->\n"
            "- [2026-09-28] Synthetic valid lesson\n")
        (self.tmp_path / "learnings.consolidated.md").write_text(
            "# Consolidated\n\n## Filter Override\n- Use primary sources\n"
            "## Domain Knowledge\n- [2026-09-28] Synthetic valid lesson\n")
        result = subprocess.run([sys.executable, str(SCRIPTS / "consolidate.py"),
                                 str(self.tmp_path), "--audit"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("raw=1/150", result.stdout)
        self.assertIn("consolidated=1/60", result.stdout)


if __name__ == "__main__":
    unittest.main()
