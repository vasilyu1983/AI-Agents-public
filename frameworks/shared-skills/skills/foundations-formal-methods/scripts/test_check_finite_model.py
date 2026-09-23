#!/usr/bin/env python3
"""Answer-level finite graph checker regressions (stdlib only)."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from check_finite_model import check_model, load_model, ModelError


def model(states, initials, edges, allowed):
    return dict(states=states, initial_states=initials, transitions=edges, invariant_states=allowed)


class CheckerTests(unittest.TestCase):
    def test_cycle_terminates(self):
        result = check_model(model(['a', 'b'], ['a'], [['a','b'], ['b','a']], ['a','b']))
        self.assertEqual(result, dict(safety_holds=True, reachable_states=['a','b'], counterexample=None, terminal_states=[]))

    def test_unreachable_violation(self):
        result = check_model(model(['a','bad'], ['a'], [], ['a']))
        self.assertTrue(result['safety_holds'])
        self.assertEqual(result['terminal_states'], ['a'])

    def test_multiinitial_shortest(self):
        result = check_model(model(['a','b','x','bad'], ['a','b'], [['a','x'],['x','bad'],['b','bad']], ['a','b','x']))
        self.assertEqual(result['counterexample'], ['b','bad'])

    def test_initial_violation(self):
        self.assertEqual(check_model(model(['bad'], ['bad'], [], []))['counterexample'], ['bad'])

    def test_edge_order_independent(self):
        edges = [['a','c'],['a','b'],['c','bad'],['b','bad']]
        first = check_model(model(['a','b','c','bad'], ['a'], edges, ['a','b','c']))
        second = check_model(model(['bad','c','b','a'], ['a'], edges[::-1], ['c','b','a']))
        self.assertEqual(first, second)
        self.assertEqual(first['counterexample'], ['a','b','bad'])

    def test_full_reachability_after_violation(self):
        result = check_model(model(['a','bad','z'], ['a'], [['a','bad'],['bad','z']], ['a','z']))
        self.assertEqual(result['reachable_states'], ['a','bad','z'])
        self.assertEqual(result['terminal_states'], ['z'])

    def test_invalid_models(self):
        valid = model(['a'], ['a'], [], ['a'])
        invalid = [None, {}, dict(valid, extra=1), dict(valid, states=[]), dict(valid, states=['a','a']),
                   dict(valid, states=[' ']), dict(valid, states=[1]), dict(valid, initial_states=[]),
                   dict(valid, initial_states=['x']), dict(valid, initial_states=['a','a']),
                   dict(valid, invariant_states=['x']), dict(valid, invariant_states=['a','a']),
                   dict(valid, transitions={}), dict(valid, transitions=[['a']]),
                   dict(valid, transitions=[['a','x']]), dict(valid, transitions=[[True,'a']]),
                   dict(valid, transitions=[['a','a'],['a','a']])]
        for candidate in invalid:
            with self.subTest(candidate=candidate), self.assertRaises(ModelError):
                check_model(candidate)

    def test_strict_json(self):
        for value in ['{"states":[],"states":[]}', '{"x":NaN}', '{"x":Infinity}', '{} trailing']:
            with self.subTest(value=value), self.assertRaises((ModelError, json.JSONDecodeError)):
                load_model(value)

    def test_cli_exit_codes(self):
        script = str(Path(__file__).with_name('check_finite_model.py'))
        for input_model, code in [(model(['a'],['a'],[],['a']),0), (model(['a'],['a'],[],[]),1), ({},2)]:
            result = subprocess.run([sys.executable, script, '-'], input=json.dumps(input_model), text=True, capture_output=True)
            self.assertEqual(result.returncode, code)
            json.loads(result.stderr if code == 2 else result.stdout)


if __name__ == '__main__':
    unittest.main()
