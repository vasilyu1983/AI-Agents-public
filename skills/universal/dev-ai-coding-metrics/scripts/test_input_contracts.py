"""Offline regression checks for accepted input and GitHub cohort boundaries."""
import argparse
import contextlib
import csv
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SCRIPTS = Path(os.environ.get('METRICS_SCRIPTS', HERE))

def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

roi = load('roi_calculator')
events = load('extract_github_events')
SAMPLE = json.loads((HERE.parent / 'data/sample-ai-metrics.json').read_text())

class InputContract(unittest.TestCase):
    def test_invalid_roi_inputs_fail_before_report(self):
        for key, values in {'team_size': [True, 1.5, -1],
                            'hours_saved_per_dev_per_week': [-1, float('nan'), '3'],
                            'avg_dev_hourly_rate': [float('inf')],
                            'ai_tooling_monthly_cost': [-5],
                            'measurement_period_weeks': [0, None],
                            'review_hours_per_dev_per_week': [-1, None],
                            'rework_hours_per_dev_per_week': [False]}.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    data = dict(SAMPLE, **{key: value})
                    with self.assertRaises(ValueError):
                        roi.calc_roi(data)

    def test_invalid_family_scores_and_signals_fail(self):
        for value in [True, 1.5, -1, 101, '70']:
            with self.subTest(score=value):
                data = json.loads(json.dumps(SAMPLE))
                data['metric_families']['quality']['score'] = value
                with self.assertRaises(ValueError):
                    roi.calc_score(data)
        for signals in ['ok', [None], None]:
            with self.subTest(signals=signals):
                data = json.loads(json.dumps(SAMPLE))
                data['metric_families']['quality']['signals'] = signals
                with self.assertRaises(ValueError):
                    roi.calc_score(data)

    def test_partial_burden_remains_incomplete(self):
        self.assertFalse(roi.calc_roi(dict(SAMPLE, review_hours_per_dev_per_week=1)).burden_included)
        self.assertTrue(roi.calc_roi(dict(SAMPLE, review_hours_per_dev_per_week=0,
                                         rework_hours_per_dev_per_week=0)).burden_included)

    def test_zero_cost_roi_is_undefined(self):
        self.assertIsNone(roi.calc_roi(dict(SAMPLE, ai_tooling_monthly_cost=0)).annualized_roi_pct)

    def test_json_root_failure_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'input.json'
            path.write_text('[]')
            result = subprocess.run([sys.executable, str(SCRIPTS/'roi_calculator.py'),
                                     'report', '--input', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('Traceback', result.stderr)
            self.assertEqual(result.stdout, '')

class GitHubContract(unittest.TestCase):
    def test_off_host_next_link_rejected(self):
        with self.assertRaises(RuntimeError):
            events._parse_next_link('<https://example.invalid/stolen>; rel="next"')

    def test_valid_next_link_with_extra_parameter(self):
        url = 'https://api.github.com/repos/example/repo/pulls?page=2'
        self.assertEqual(events._parse_next_link(f'<{url}>; rel="next"; type="application/json"'), url)

    def test_wrong_page_shape_rejected(self):
        with patch.object(events, '_get', return_value=({}, {})):
            with self.assertRaises(RuntimeError):
                list(events._paginate('https://api.github.com/repos/example/repo/pulls'))

    def test_all_pr_outcomes_preserved(self):
        rows = [dict(number=i, user={'login': 'synthetic'}, created_at='2026-09-01T00:00:00Z',
                     state=state, merged_at=merged)
                for i, (state, merged) in enumerate([('open', None), ('closed', None),
                                                   ('closed', '2026-09-02T00:00:00Z')], 1)]
        captured = io.StringIO()
        args = argparse.Namespace(repo='example/repo', since='2026-09-01', output=None)
        with patch.object(events, '_paginate', return_value=iter([rows])) as paginate, \
             patch.object(events, '_fetch_pr_details', return_value={'additions': 1, 'deletions': 0, 'changed_files': 1}), \
             patch.object(events, '_fetch_pr_reviews', return_value=[]), \
             contextlib.redirect_stdout(captured):
            events.cmd_pulls(args)
        self.assertIn('state=all', paginate.call_args.args[0])
        exported = list(csv.DictReader(io.StringIO(captured.getvalue())))
        self.assertEqual(len(exported), 3)
        self.assertEqual([row['outcome'] for row in exported], ['still_open', 'closed_unmerged', 'merged'])

    def test_unknown_pr_state_cannot_invent_outcome(self):
        row = dict(number=1, created_at='2026-09-01T00:00:00Z', merged_at=None)
        args = argparse.Namespace(repo='example/repo', since='2026-09-01', output=None)
        with patch.object(events, '_paginate', return_value=iter([[row]])), \
             patch.object(events, '_fetch_pr_details', return_value={'additions': 1, 'deletions': 0, 'changed_files': 1}), \
             patch.object(events, '_fetch_pr_reviews', return_value=[]):
            with self.assertRaises(RuntimeError):
                events.cmd_pulls(args)

    def test_mid_export_failure_preserves_existing_file(self):
        def pages(url):
            yield []
            raise RuntimeError('synthetic network failure')
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'output.csv'
            out.write_text('existing result')
            args = argparse.Namespace(repo='example/repo', since='2026-09-01', output=str(out))
            with patch.object(events, '_paginate', side_effect=pages):
                with self.assertRaises(RuntimeError):
                    events.cmd_pulls(args)
            self.assertEqual(out.read_text(), 'existing result')

if __name__ == '__main__':
    unittest.main()
