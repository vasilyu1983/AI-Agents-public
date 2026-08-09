#!/usr/bin/env python3

"""Tests for check_local_links.py.

Run: python3 -m unittest scripts.test_check_local_links -v
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

import check_local_links as cll  # noqa: E402


class StripCodeTests(unittest.TestCase):
    def test_fenced_block_removed(self):
        text = "before\n```js\nconst [x] = a;\nres.get('/api')\n```\nafter\n"
        stripped = cll._strip_code(text)
        self.assertNotIn("res.get", stripped)
        self.assertNotIn("[x]", stripped)
        self.assertIn("before", stripped)
        self.assertIn("after", stripped)

    def test_tilde_fenced_block_removed(self):
        text = "before\n~~~\n[x][y]\n~~~\nafter\n"
        self.assertNotIn("[x][y]", cll._strip_code(text))

    def test_inline_code_removed(self):
        text = "use `res.get('/api')` and `[x]` here"
        self.assertNotIn("res.get", cll._strip_code(text))

    def test_indented_code_removed(self):
        text = "para\n\n    [x] indented code\n\nafter"
        self.assertNotIn("[x] indented", cll._strip_code(text))

    def test_real_link_outside_code_preserved(self):
        text = "see [README](./README.md) and `code` here"
        self.assertIn("[README](./README.md)", cll._strip_code(text))


class CollectTargetsTests(unittest.TestCase):
    def test_inline_link_collected(self):
        targets = cll._collect_targets("[a](./a.md)")
        self.assertIn("./a.md", targets)

    def test_code_block_link_ignored(self):
        text = "real [a](./a.md)\n\n```\n[b](./b.md)\n```\n"
        targets = cll._collect_targets(text)
        self.assertIn("./a.md", targets)
        self.assertNotIn("./b.md", targets)

    def test_checkbox_not_treated_as_reference(self):
        text = "- [x] done\n- [ ] todo\n"
        targets = cll._collect_targets(text)
        self.assertEqual(targets, [])

    def test_reference_style_link(self):
        text = "see [foo][1]\n\n[1]: ./foo.md"
        self.assertIn("./foo.md", cll._collect_targets(text))

    def test_external_filtered_separately(self):
        # _collect_targets returns raw; _is_external_link filters.
        targets = cll._collect_targets("[a](https://example.com)")
        self.assertTrue(all(cll._is_external_link(t) for t in targets))


class FindMissingLocalLinksTests(unittest.TestCase):
    def test_missing_target_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("[broken](./missing.md)")
            missing = cll.find_missing_local_links(root)
            self.assertEqual(len(missing), 1)
            self.assertEqual(missing[0].target, "./missing.md")

    def test_existing_target_not_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("[ok](./b.md)")
            (root / "b.md").write_text("# B")
            self.assertEqual(cll.find_missing_local_links(root), [])

    def test_code_block_does_not_create_false_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text(
                "# Doc\n\n```js\nconst [...args] = res.get('/missing.md')\n```\n"
            )
            self.assertEqual(cll.find_missing_local_links(root), [])


if __name__ == "__main__":
    unittest.main()
