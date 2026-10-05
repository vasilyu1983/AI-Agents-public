#!/usr/bin/env python3
"""Offline regression checks for stale imports and incomplete validation inputs."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


examples = load('examples', os.environ.get('LOCALISATION_CHECK_EXAMPLES', HERE / 'check_examples.py'))
urls = load('urls', os.environ.get('LOCALISATION_CHECK_URLS', HERE / 'check_urls.py'))


class CheckRegressions(unittest.TestCase):
    def run_examples(self, text):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            rules = [(root / path.relative_to(examples.ROOT), pattern, message)
                     for path, pattern, message in examples.RULES]
            for path, _, _ in rules:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('')
            (root / 'assets').mkdir(exist_ok=True)
            (root / 'references').mkdir(exist_ok=True)
            (root / 'references' / 'fixture.md').write_text(text)
            with patch.object(examples, 'ROOT', root), patch.object(examples, 'RULES', rules), contextlib.redirect_stdout(io.StringIO()):
                return examples.main()

    def test_old_macro_import_rejected(self):
        self.assertEqual(self.run_examples('import {t} from "@lingui/macro";'), 1)

    def test_multiline_old_macro_import_rejected(self):
        self.assertEqual(self.run_examples("import {\n t,\n msg\n} from\n '@lingui/macro';"), 1)

    def test_dynamic_old_macro_import_rejected(self):
        self.assertEqual(self.run_examples("const macros = import('@lingui/macro');"), 1)

    def test_commonjs_old_macro_import_rejected(self):
        self.assertEqual(self.run_examples("const macros = require('@lingui/macro');"), 1)

    def test_replacement_imports_and_migration_prose_pass(self):
        self.assertEqual(self.run_examples("import {t} from '@lingui/core/macro';\nimport {Trans} from '@lingui/react/macro';\nThe `@lingui/macro` package is deprecated."), 0)

    def test_missing_example_directories_cannot_pass(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(examples, 'ROOT', Path(folder)), patch.object(examples, 'RULES', []), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(examples.main(), 2)

    def test_empty_source_catalog_cannot_pass(self):
        for value in ({}, {'categories': {}}, {'categories': {'docs': []}}):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as folder:
                source = Path(folder) / 'sources.json'
                source.write_text(json.dumps(value))
                with patch.object(urls, 'SOURCES', source), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(urls.main(), 2)


if __name__ == '__main__':
    unittest.main()
