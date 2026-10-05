"""Regression checks for revision inspection using small OOXML fixtures."""

import tempfile
import unittest
import zipfile
from pathlib import Path

from docx_inspect_ooxml import inspect_docx


class InspectDocxTests(unittest.TestCase):
    def _package(self, directory: str, document_xml: str) -> Path:
        path = Path(directory) / "sample.docx"
        with zipfile.ZipFile(path, "w") as package:
            package.writestr("word/document.xml", document_xml)
        return path

    def test_revision_with_equivalent_namespace_prefix_is_counted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self._package(
                directory,
                '<x:document xmlns:x="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                '<x:body><x:p><x:ins><x:r><x:t>Added</x:t></x:r></x:ins></x:p></x:body>'
                '</x:document>',
            )
            self.assertEqual(inspect_docx(path).counts["w:ins"], 1)

    def test_malformed_document_xml_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self._package(directory, "<w:document>")
            with self.assertRaisesRegex(ValueError, "word/document.xml"):
                inspect_docx(path)

    def test_non_document_xml_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self._package(
                directory,
                '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>',
            )
            with self.assertRaisesRegex(ValueError, "word/document.xml"):
                inspect_docx(path)


if __name__ == "__main__":
    unittest.main()
