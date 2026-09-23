import copy
import json
from pathlib import Path
import unittest
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

    def test_reject_unknown_and_malformed(self):
        for mutate in [lambda m: m['plan'].append('invented'), lambda m: m['actions']['close']['add'].append('ticket-open'), lambda m: m['actions']['close'].update(cost=True), lambda m: m.update(extra=1), lambda m: m['initial'].append('authorized')]:
            with self.subTest(mutate=mutate):
                model = copy.deepcopy(self.model)
                mutate(model)
                with self.assertRaises(ValueError):
                    replay_plan.replay(model)


if __name__ == '__main__':
    unittest.main()
