import tempfile
import unittest
from pathlib import Path

import check_cc_ids

CATALOG = """
| ID | Rule |
|---|---|
| CC-SEC-01 | secrets |
| CC-SEC-05 | deps |
| CC-FUN-01 | single purpose |
"""


class CheckCcIdsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.catalog = self.root / "catalog.md"
        self.catalog.write_text(CATALOG)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        p = self.root / name
        p.write_text(text)
        return p

    def test_valid_ids_and_wildcards_pass(self):
        doc = self.write("ok.md", "Cite CC-SEC-01 and CC-FUN-01; see CC-SEC-* rules.")
        problems, n = check_cc_ids.check([doc], self.catalog)
        self.assertEqual(problems, [])
        self.assertEqual(n, 3)

    def test_three_digit_and_unknown_category_fail(self):
        # The exact bug class the 2026-09 audit found in SKILL.md.
        doc = self.write("bad.md", "e.g. CC-SEC-001 and CC-COMPLEXITY-* and CC-DEP-01")
        problems, _ = check_cc_ids.check([doc], self.catalog)
        self.assertEqual(len(problems), 3)
        self.assertTrue(any("CC-SEC-001" in p for p in problems))
        self.assertTrue(any("CC-COMPLEXITY-*" in p for p in problems))
        self.assertTrue(any("CC-DEP-01" in p for p in problems))

    def test_license_tokens_are_not_rule_ids(self):
        doc = self.write("lic.md", "Licensed CC-BY-4.0 / CC-BY-SA; dataset CC-MAIN-2024-10.")
        problems, _ = check_cc_ids.check([doc], self.catalog)
        self.assertEqual(problems, [])

    def test_learnings_files_skipped_in_directory_scan(self):
        self.write("learnings.md", "historical: CC-SEC-001")
        problems, _ = check_cc_ids.check([self.root], self.catalog)
        self.assertEqual(problems, [])

    def test_empty_catalog_fails_closed(self):
        self.catalog.write_text("no table here")
        doc = self.write("ok.md", "CC-SEC-01")
        with self.assertRaises(ValueError):
            check_cc_ids.check([doc], self.catalog)

    def test_missing_path_fails_closed(self):
        with self.assertRaises(FileNotFoundError):
            check_cc_ids.check([self.root / "nope.md"], self.catalog)

    def test_main_exit_codes(self):
        self.assertEqual(check_cc_ids.main([str(self.root / "missing.md")]), 2)


if __name__ == "__main__":
    unittest.main()
