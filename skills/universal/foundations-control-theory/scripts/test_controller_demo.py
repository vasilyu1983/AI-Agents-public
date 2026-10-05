#!/usr/bin/env python3
"""Offline fail-closed and recovery-metric regressions for the PI demonstration."""
import importlib.util
import math
import os
from pathlib import Path
import unittest


source = Path(os.environ.get('CONTROLLER_DEMO_UNDER_TEST',
                            Path(__file__).with_name('controller_demo.py')))
spec = importlib.util.spec_from_file_location('controller_demo_under_test', source)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class ControllerDemoTests(unittest.TestCase):
    def test_nonfinite_inputs_fail_before_command(self):
        valid = [0., 1., 1., .2, .1, 0., 1.]
        for index in range(len(valid)):
            for value in (math.nan, math.inf, -math.inf):
                with self.subTest(index=index, value=value):
                    args = valid.copy()
                    args[index] = value
                    with self.assertRaises(ValueError):
                        demo.integral_step(*args)

    def test_overflow_fails_before_command(self):
        cases = [
            (0., 1e308, 1e308, 0., .1, 0., 1.),
            (0., 1e308, 0., 1e308, .1, 0., 1.),
            (1e308, 1e308, 0., 1., 1., -1e308, 1.7e308),
        ]
        for args in cases:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    demo.integral_step(*args)

    def test_recovery_metric_excludes_initial_offset(self):
        protected, unprotected = demo.simulate(), demo.simulate(False)
        self.assertLess(protected['post_crossing_excess'], .1)
        self.assertIsNone(unprotected['post_crossing_excess'])

    def test_existing_directional_and_replay_checks(self):
        self.assertEqual(len(demo.self_test()), 2)


if __name__ == '__main__':
    unittest.main()
