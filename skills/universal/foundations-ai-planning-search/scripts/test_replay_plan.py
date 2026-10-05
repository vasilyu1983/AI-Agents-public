import copy
import json
from pathlib import Path
import unittest
import subprocess
import sys
import tempfile
import replay_plan


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads((Path(__file__).resolve().parent.parent / 'data/plan-fixtures.json').read_text())

    def test_valid_cost_and_goal(self):
        result = replay_plan.replay(self.model)
        self.assertEqual(result['status'], 'goal')
        self.assertEqual(result['cost'], 3)
        self.assertNotIn('ticket-open', result['state'])

    def test_failed_order(self):
        self.model['plan'] = ['close']
        result = replay_plan.replay(self.model)
        self.assertEqual(result['missing'], ['reviewed'])
        self.assertEqual(result['cost'], 0)

    def test_drift_stops_after_verified_progress(self):
        self.model['initial'].remove('authorized')
        result = replay_plan.replay(self.model)
        self.assertEqual(result['step'], 1)
        self.assertEqual(result['cost'], 1)
        self.assertNotIn('ticket-closed', result['state'])

    def test_unmet_goal_not_proof_of_infeasibility(self):
        self.model['goal'].append('unmodeled-goal')
        self.assertEqual(replay_plan.replay(self.model)['status'], 'goal-unmet')

    def test_cli_rejects_duplicate_preconditions(self):
        self.model['initial'].remove('authorized')
        self.model['plan'] = ['close']
        payload = json.dumps(self.model).replace(
            '"requires": ["reviewed", "authorized"]',
            '"requires": ["reviewed", "authorized"], "requires": []')
        self.assertNotEqual(payload, json.dumps(self.model))
        with tempfile.TemporaryDirectory() as directory:
            model_path = Path(directory) / 'duplicate.json'
            model_path.write_text(payload, encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(Path(replay_plan.__file__).resolve()), str(model_path)],
                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn('duplicate JSON field: requires', result.stderr)
        self.assertEqual(result.stdout, '')

    def test_reject_unknown_and_malformed(self):
        for mutate in [lambda m: m['plan'].append('invented'), lambda m: m['actions']['close']['add'].append('ticket-open'), lambda m: m['actions']['close'].update(cost=True), lambda m: m.update(extra=1), lambda m: m['initial'].append('authorized')]:
            with self.subTest(mutate=mutate):
                model = copy.deepcopy(self.model)
                mutate(model)
                with self.assertRaises(ValueError):
                    replay_plan.replay(model)


if __name__ == '__main__':
    unittest.main()
