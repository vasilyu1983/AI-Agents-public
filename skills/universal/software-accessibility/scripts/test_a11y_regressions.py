#!/usr/bin/env python3
"""Offline claims/report regressions. A11Y_SCRIPT_DIR permits baseline comparison."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(os.environ.get('A11Y_SCRIPT_DIR', Path(__file__).resolve().parent))


class ClaimsTests(unittest.TestCase):
    def template(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / 'check_a11y_baseline.py'), '--generate-template'], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def check(self, claims):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'claims.json'
            path.write_text(json.dumps(claims))
            return subprocess.run([sys.executable, str(SCRIPTS / 'check_a11y_baseline.py'), '--claims', str(path)], capture_output=True, text=True)

    def evidence(self):
        claims = self.template()
        for entry in claims['addressed']:
            entry.update(status='pass', note='Fixture records manual verification for this criterion.')
        return claims

    def test_generated_template_does_not_pass(self):
        self.assertNotEqual(self.check(self.template()).returncode, 0)

    def test_complete_evidence_passes(self):
        self.assertEqual(self.check(self.evidence()).returncode, 0)

    def test_unknown_criterion_rejected(self):
        claims = self.evidence()
        claims['addressed'].append({'sc': '9.9.9', 'status': 'pass', 'note': 'Typo'})
        self.assertEqual(self.check(claims).returncode, 2)

    def test_duplicate_cannot_mask_failure(self):
        claims = self.evidence()
        failed = dict(claims['addressed'][0], status='fail')
        claims['addressed'].insert(0, failed)
        self.assertEqual(self.check(claims).returncode, 2)

    def test_pass_requires_evidence(self):
        claims = self.evidence()
        claims['addressed'][0]['note'] = ''
        self.assertEqual(self.check(claims).returncode, 2)

    def test_na_requires_rationale(self):
        claims = self.evidence()
        claims['addressed'][0].update(status='na', note='')
        self.assertEqual(self.check(claims).returncode, 2)

    def test_invalid_types_report_input_error(self):
        claims = self.evidence()
        claims['addressed'][0]['sc'] = 42
        result = self.check(claims)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)


class AxeTests(unittest.TestCase):
    def run_stub(self, report, code=0, stale=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            if stale:
                (root / 'axe-report-20000101T000000.json').write_text(json.dumps(self.clean()))
                date = root / 'date'
                date.write_text('#!/usr/bin/env bash\nprintf \"20000101T000000\\n\"\n')
                date.chmod(0o755)
            stub = root / 'npx'
            stub.write_text('#!/usr/bin/env python3\nimport json, os, pathlib, sys\na=sys.argv\np=a[a.index("--save")+1]\nr=json.loads(os.environ["TEST_REPORT"])\nif r is not None: pathlib.Path(p).write_text(json.dumps(r))\nsys.exit(int(os.environ["TEST_EXIT"]))\n')
            stub.chmod(0o755)
            env = dict(os.environ, PATH=str(root) + os.pathsep + os.environ['PATH'], TEST_REPORT=json.dumps(report), TEST_EXIT=str(code))
            return subprocess.run(['bash', str(SCRIPTS / 'run_axe.sh'), 'https://example.com'], cwd=root, env=env, text=True, capture_output=True)

    def clean(self):
        return [{'violations': [], 'passes': [{'id': 'document-title'}], 'incomplete': [], 'inapplicable': []}]

    def test_valid_clean_scan_passes(self):
        self.assertEqual(self.run_stub(self.clean()).returncode, 0)

    def test_missing_report_fails(self):
        self.assertNotEqual(self.run_stub(None).returncode, 0)

    def test_stale_clean_report_cannot_mask_missing_new_scan(self):
        self.assertNotEqual(self.run_stub(None, stale=True).returncode, 0)

    def test_empty_report_fails(self):
        self.assertNotEqual(self.run_stub([]).returncode, 0)

    def test_no_rules_exercised_fails(self):
        report = self.clean()
        report[0]['passes'] = []
        self.assertNotEqual(self.run_stub(report).returncode, 0)

    def test_violation_despite_exit_zero_fails(self):
        report = self.clean()
        report[0]['violations'] = [{'id': 'label'}]
        self.assertNotEqual(self.run_stub(report).returncode, 0)

    def test_cli_failure_fails(self):
        self.assertNotEqual(self.run_stub(None, 3).returncode, 0)


if __name__ == '__main__':
    unittest.main()
