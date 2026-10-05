"""Regression checks for package failures that must block release."""

import tempfile
import unittest
import zipfile
from pathlib import Path

from docx_quality_gate import quality_gate


DOCUMENT = (
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:body/></w:document>'
)


class QualityGateTests(unittest.TestCase):
    def _package(self, directory: str, name: str, include_opc: bool) -> Path:
        path = Path(directory) / name
        with zipfile.ZipFile(path, "w") as package:
            package.writestr("word/document.xml", DOCUMENT)
            if include_opc:
                package.writestr(
                    "[Content_Types].xml",
                    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
                )
                package.writestr(
                    "_rels/.rels",
                    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>',
                )
        return path

    def test_non_word_extension_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self._package(directory, "sample.txt", include_opc=True)
            self.assertFalse(quality_gate(path, 10, False)["passed"])

    def test_missing_package_manifest_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self._package(directory, "sample.docx", include_opc=False)
            self.assertFalse(quality_gate(path, 10, False)["passed"])


if __name__ == "__main__":
    unittest.main()
