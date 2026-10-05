"""Failure-path regressions; run with --script to test a pre-change snapshot."""
from __future__ import annotations

import argparse
from datetime import datetime
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

parser = argparse.ArgumentParser()
parser.add_argument("--script", type=Path, default=Path(__file__).with_name("scrub_metadata.py"))
args, remaining = parser.parse_known_args()
spec = importlib.util.spec_from_file_location("scrub_under_test", args.script)
scrub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scrub)


class ScrubTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / "input.pdf"
        self.source.write_bytes(b"synthetic input")
        self.output = Path(self.tmp.name) / "output.pdf"
        self.doc = SimpleNamespace(needs_pass=False, is_pdf=True)
        self.doc.scrub = unittest.mock.Mock()
        self.doc.close = unittest.mock.Mock()
        self.doc.save = lambda path, **kw: Path(path).write_bytes(b"synthetic scrubbed output")

    def run_main(self, *options, system="Darwin", **patches):
        with patch.object(sys, "argv", ["scrub_metadata.py", str(self.source), str(self.output), *options]), \
             patch.object(scrub.platform, "system", return_value=system), \
             patch.dict(sys.modules, {"pymupdf": SimpleNamespace(open=lambda *a, **k: self.doc)}):
            from contextlib import ExitStack
            with ExitStack() as stack:
                for name, value in patches.items():
                    stack.enter_context(patch.object(scrub, name, value))
                try:
                    return scrub.main()
                except SystemExit as exc:
                    return exc.code
                except Exception:
                    return "unhandled exception"

    def test_invalid_date_does_not_publish(self):
        self.assertNotEqual(self.run_main("--filesystem-date", "2026-02-30"), 0)
        self.assertFalse(self.output.exists())

    def test_xattr_failure_preserves_existing_output(self):
        self.output.write_bytes(b"original output")
        failure = unittest.mock.Mock(side_effect=OSError("attribute cleanup denied"))
        self.assertNotEqual(self.run_main("--strip-xattrs", strip_macos_xattrs=failure), 0)
        self.assertEqual(self.output.read_bytes(), b"original output")

    def test_xattrs_unsupported_platform_rejected(self):
        self.assertNotEqual(self.run_main("--strip-xattrs", system="Linux"), 0)
        self.assertFalse(self.output.exists())

    def test_setfile_failure_is_not_ignored(self):
        def failed_command(command, **kwargs):
            if kwargs.get("check"):
                raise subprocess.CalledProcessError(1, command)
            return subprocess.CompletedProcess(command, 1)
        with patch.object(scrub.platform, "system", return_value="Darwin"), \
             patch.object(scrub.subprocess, "run", side_effect=failed_command):
            self.assertNotEqual(self.run_main("--filesystem-date", "2026-09-28"), 0)
        self.assertFalse(self.output.exists())

    def test_xattrs_use_native_checked_command(self):
        with patch.object(scrub.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout="")) as run:
            scrub.strip_macos_xattrs(self.source)
        self.assertEqual(run.call_args_list[0].args[0], ["xattr", "-c", str(self.source)])
        self.assertTrue(all(call.kwargs.get("check") for call in run.call_args_list))

    def test_residual_xattrs_fail_closed(self):
        result = subprocess.CompletedProcess([], 0, stdout="com.apple.provenance\n")
        with patch.object(scrub.subprocess, "run", return_value=result):
            with self.assertRaises(OSError):
                scrub.strip_macos_xattrs(self.source)

    def test_non_pdf_rejected_before_scrub(self):
        self.doc.is_pdf = False
        self.assertNotEqual(self.run_main(), 0)
        self.assertFalse(self.output.exists())
        self.doc.scrub.assert_not_called()

    def test_default_retains_ocr_links_and_form_fields(self):
        self.assertEqual(self.run_main(), 0)
        options = self.doc.scrub.call_args.kwargs
        for flag in ("hidden_text", "remove_links", "reset_fields", "reset_responses", "redactions"):
            self.assertFalse(options[flag])
        self.assertEqual(self.output.read_bytes(), b"synthetic scrubbed output")

    def test_scrub_failure_does_not_publish(self):
        self.doc.scrub.side_effect = RuntimeError("scrub failed")
        self.assertNotEqual(self.run_main(), 0)
        self.assertFalse(self.output.exists())


try:
    import pymupdf
except ImportError:
    pymupdf = None


@unittest.skipIf(pymupdf is None, "PyMuPDF needed for real PDF integration tests")
class RealPdfTests(unittest.TestCase):
    def run_scrub(self, *options):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        source = Path(tmp.name) / "input.pdf"
        output = Path(tmp.name) / "output.pdf"
        with pymupdf.open() as doc:
            page = doc.new_page()
            page.insert_text((40, 40), "visible synthetic content")
            page.insert_text((40, 80), "hidden synthetic OCR", render_mode=3)
            page.insert_link({"kind": pymupdf.LINK_URI, "from": pymupdf.Rect(40, 30, 180, 45), "uri": "https://example.com"})
            doc.set_metadata({"author": "synthetic author"})
            doc.embfile_add("synthetic.txt", b"synthetic attachment")
            doc.save(source)
        result = subprocess.run([sys.executable, str(args.script), str(source), str(output), *options], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return output

    def test_real_pdf_preserves_content_and_clears_metadata(self):
        output = self.run_scrub()
        with pymupdf.open(output) as doc:
            self.assertIn("visible synthetic content", doc[0].get_text())
            self.assertIn("hidden synthetic OCR", doc[0].get_text())
            self.assertEqual(len(doc[0].get_links()), 1)
            self.assertFalse(doc.metadata.get("author"))
            self.assertEqual(doc.embfile_count(), 0)

    @unittest.skipUnless(sys.platform == "darwin", "native macOS filesystem checks")
    def test_real_pdf_native_filesystem_options(self):
        output = self.run_scrub("--filesystem-date", "2026-09-28")
        expected = datetime(2026, 9, 28, 12).timestamp()
        self.assertAlmostEqual(output.stat().st_mtime, expected, delta=1)

    @unittest.skipUnless(sys.platform == "darwin", "native macOS filesystem checks")
    def test_real_xattr_cleanup_or_explicit_refusal(self):
        source = self.run_scrub()
        destination = source.with_name("destination.pdf")
        destination.write_bytes(b"previous output")
        result = subprocess.run([sys.executable, str(args.script), str(source), str(destination), "--strip-xattrs"], capture_output=True, text=True)
        if result.returncode == 0:
            remaining = subprocess.run(["xattr", str(destination)], capture_output=True, text=True, check=True).stdout
            self.assertEqual(remaining, "")
        else:
            self.assertEqual(result.returncode, 1)
            self.assertIn("Extended attributes remain", result.stderr)
            self.assertEqual(destination.read_bytes(), b"previous output")


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], *remaining])
