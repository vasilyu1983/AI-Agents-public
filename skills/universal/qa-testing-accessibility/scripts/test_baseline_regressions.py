"""Offline baseline regressions using Node's TypeScript stripping and mock adapters.

Run with Node 24+ on PATH: python3 scripts/test_baseline_regressions.py
Pass --script /path/to/old.ts to demonstrate pre-fix failures.
No browsers, network, application, or package installation is involved.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('generate-a11y-baseline.ts').resolve()


class BaselineRegressionTests(unittest.TestCase):
    def run_scan(self, **settings):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output = root / 'baseline.json'
            output.write_text('prior baseline\n')
            (root / 'playwright.mjs').write_text('''
export const chromium = {launch: async () => ({
  newPage: async () => ({goto: async (url) => {
    const status = process.env.MOCK_STATUS ?? '200';
    if (status === 'none') return null;
    return {ok: () => Number(status) >= 200 && Number(status) < 300,
            status: () => Number(status)};
  }}), close: async () => {}
})};
''')
            (root / 'axe.mjs').write_text('''
export default class AxeBuilder {
  withTags(tags) { return this; }
  async analyze() { return {violations: [{id: 'label', impact: 'serious',
    description: 'fixture', nodes: [{target: ['#submit']}]}]}; }
}
''')
            (root / 'loader.mjs').write_text('''
export async function resolve(specifier, context, next) {
  const mock = {'@playwright/test': './playwright.mjs', '@axe-core/playwright': './axe.mjs'}[specifier];
  if (mock) return {url: new URL(mock, import.meta.url).href, shortCircuit: true};
  return next(specifier, context);
}
''')
            env = {key: value for key, value in os.environ.items()
                   if key not in {'BASE_URL', 'PATHS', 'OUT_FILE', 'AXE_TAGS', 'MOCK_STATUS'}}
            env.update(BASE_URL='https://example.test', PATHS='/checkout', OUT_FILE=str(output))
            env.update(settings)
            result = subprocess.run(
                ['node', '--experimental-strip-types', '--experimental-loader',
                 str(root / 'loader.mjs'), str(SCRIPT)], env=env,
                capture_output=True, text=True, timeout=20, cwd=root)
            return result, output.read_text()

    def test_success_writes_per_node_fingerprint(self):
        result, baseline = self.run_scan()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(baseline)[0]['fingerprints'], ['label|/checkout|["#submit"]'])

    def test_http_failure_preserves_baseline(self):
        for status in ['404', '503', 'none']:
            with self.subTest(status=status):
                result, baseline = self.run_scan(MOCK_STATUS=status)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Scan failed for /checkout', result.stderr)
                self.assertEqual(baseline, 'prior baseline\n')

    def test_malformed_paths_fail_before_scan(self):
        for paths in ['', '//other.test', 'checkout', '/,/login,', '/\\other.test', '/\n/other.test', '/checkout#part']:
            with self.subTest(paths=paths):
                result, baseline = self.run_scan(PATHS=paths)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('PATHS', result.stderr)
                self.assertEqual(baseline, 'prior baseline\n')

    def test_malformed_base_url_fails_before_scan(self):
        for base in ['', 'example.test', 'ftp://example.test', 'https://user:password@example.test',
                     'https://example.test?query=x', 'https://example.test#part']:
            with self.subTest(base=base):
                result, baseline = self.run_scan(BASE_URL=base)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('BASE_URL', result.stderr)
                self.assertEqual(baseline, 'prior baseline\n')

    def test_empty_tags_and_output_fail(self):
        for key, value in [('AXE_TAGS', ''), ('AXE_TAGS', 'wcag2a,'), ('OUT_FILE', ' ')]:
            with self.subTest(key=key, value=value):
                result, baseline = self.run_scan(**{key: value})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(key, result.stderr)
                self.assertEqual(baseline, 'prior baseline\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--script', type=Path)
    arguments, remaining = parser.parse_known_args()
    if arguments.script:
        SCRIPT = arguments.script.resolve()
    if not shutil.which('node'):
        parser.error('Node 24+ is required for offline TypeScript tests')
    unittest.main(argv=[__file__, *remaining])
