#!/usr/bin/env python3
"""Failure-path regressions; XLSX_SANITIZER_SCRIPT can select an old sanitizer."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET
import zipfile

SCRIPT = Path(os.environ.get("XLSX_SANITIZER_SCRIPT", str(Path(__file__).with_name("xlsx_sanitize.py"))))
MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT = "http://schemas.openxmlformats.org/package/2006/content-types"


class SanitizeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "input.xlsx"
        self.output = self.root / "output.xlsx"

    def package(self, malformed=False):
        with zipfile.ZipFile(self.source, "w") as z:
            z.writestr("xl/workbook.xml", f'<workbook xmlns="{MAIN}"><externalReferences/></workbook>')
            z.writestr("xl/_rels/workbook.xml.rels", f'<Relationships xmlns="{REL}"><Relationship Id="r1" Type="example/externalLink" Target="externalLinks/link.xml"/></Relationships>')
            z.writestr("[Content_Types].xml", f'<Types xmlns="{CONTENT}"><Override PartName="/xl/externalLinks/link.xml" ContentType="example"/></Types>')
            z.writestr("xl/sharedStrings.xml", f'<sst xmlns="{MAIN}"><si><t>=danger</t></si></sst>')
            z.writestr("xl/worksheets/sheet1.xml", "<broken" if malformed else f'<worksheet xmlns="{MAIN}"><sheetData><row><c r="A1" t="inlineStr"><is><t>+text</t></is></c><c r="B1"><f>1+1</f><v>2</v></c></row></sheetData></worksheet>')
            z.writestr("xl/externalLinks/link.xml", "link")

    def run_script(self, output=None):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.source), str(output or self.output), "--strip-external-links"], capture_output=True, text=True)

    def test_success_keeps_formula_quotes_text_and_removes_links(self):
        self.package()
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(self.output) as z:
            self.assertNotIn("xl/externalLinks/link.xml", z.namelist())
            shared = ET.fromstring(z.read("xl/sharedStrings.xml"))
            self.assertEqual(shared.find(f".//{{{MAIN}}}t").text, "'=danger")
            sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
            self.assertEqual(sheet.find(f".//{{{MAIN}}}t").text, "'+text")
            self.assertEqual(sheet.find(f".//{{{MAIN}}}f").text, "1+1")
            self.assertEqual(len(ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))), 0)
            self.assertEqual(len(ET.fromstring(z.read("[Content_Types].xml"))), 0)
        self.assertEqual(set(self.root.iterdir()), {self.source, self.output})

    def test_malformed_xml_leaves_no_output(self):
        self.package(malformed=True)
        self.assertEqual(self.run_script().returncode, 2)
        self.assertEqual(set(self.root.iterdir()), {self.source})

    def test_malformed_xml_preserves_existing_output(self):
        self.package(malformed=True)
        self.output.write_bytes(b"existing output")
        self.assertEqual(self.run_script().returncode, 2)
        self.assertEqual(self.output.read_bytes(), b"existing output")
        self.assertEqual(set(self.root.iterdir()), {self.source, self.output})

    def test_missing_workbook_is_rejected(self):
        with zipfile.ZipFile(self.source, "w") as z:
            z.writestr("word/document.xml", "<document/>")
        self.assertEqual(self.run_script().returncode, 2)
        self.assertFalse(self.output.exists())

    def test_symlink_alias_cannot_overwrite_input(self):
        self.package()
        original = self.source.read_bytes()
        self.output.symlink_to(self.source)
        self.assertEqual(self.run_script().returncode, 2)
        self.assertEqual(self.source.read_bytes(), original)

    def test_hardlink_alias_cannot_overwrite_input(self):
        self.package()
        original = self.source.read_bytes()
        self.output.hardlink_to(self.source)
        self.assertEqual(self.run_script().returncode, 2)
        self.assertEqual(self.source.read_bytes(), original)

    def test_bad_zip_leaves_no_output(self):
        self.source.write_bytes(b"not a zip")
        self.assertEqual(self.run_script().returncode, 2)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
