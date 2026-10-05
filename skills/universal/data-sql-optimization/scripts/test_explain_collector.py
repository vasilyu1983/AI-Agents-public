#!/usr/bin/env python3
"""Offline regressions. EXPLAIN_COLLECTOR_MODULE can point to an old snapshot."""
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

path = Path(os.environ.get('EXPLAIN_COLLECTOR_MODULE', Path(__file__).with_name('explain_collector.py')))
spec = importlib.util.spec_from_file_location('collector', path)
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
PLAN = [{"Plan": {"Node Type": "Result", "Total Cost": 1}}]


class CollectorRegressionTests(unittest.TestCase):
    def test_default_does_not_execute(self):
        with patch.object(sys, 'argv', ['collector']), \
             patch.object(collector, '_get_database_url', return_value='unused'), \
             patch.object(collector, '_load_queries', return_value=['SELECT 1']), \
             patch.object(collector, 'collect_plans', return_value=0) as collect:
            collector.main()
        self.assertFalse(collect.call_args.args[2])

    def test_no_analyze_options_are_portable(self):
        commands = collector._build_explain_commands('SELECT 1', False, 30)
        self.assertEqual(commands[2], 'EXPLAIN (FORMAT JSON) SELECT 1')

    def test_analyze_requires_explicit_flag(self):
        args = collector.build_parser().parse_args(['--analyze'])
        self.assertTrue(args.analyze)

    def test_rejects_multiple_statements_before_psql(self):
        output = io.StringIO()
        with patch.object(collector, '_run_psql', return_value=(json.dumps(PLAN), '', 0)) as run:
            failures = collector.collect_plans(['SELECT 1; COMMIT; DELETE FROM items'], 'unused', False, 1, output)
        run.assert_not_called()
        self.assertEqual(failures, 1)
        self.assertFalse(json.loads(output.getvalue())['success'])

    def test_extra_terminator_is_not_stripped(self):
        query = collector._strip_query('SELECT 1;;')
        with self.assertRaises(ValueError):
            collector._build_explain_commands(query, False, 1)

    def test_internal_literal_semicolon_is_rejected_conservatively(self):
        with self.assertRaises(ValueError):
            collector._build_explain_commands("SELECT ';'", False, 1)

    def test_non_plan_json_fails_closed(self):
        for value in ({}, [], [1], [{"Plan": {}}], [{"Plan": {"Node Type": ""}}], True, 1):
            with self.subTest(value=value):
                self.assertIsNone(collector._parse_plan_json(json.dumps(value)))

    def test_invalid_json_is_failed_record(self):
        output = io.StringIO()
        with patch.object(collector, '_run_psql', return_value=('{}', '', 0)):
            failures = collector.collect_plans(['SELECT 1'], 'unused', False, 1, output)
        self.assertEqual(failures, 1)
        self.assertFalse(json.loads(output.getvalue())['success'])

    def test_valid_plan_with_command_tags_is_kept(self):
        self.assertEqual(collector._parse_plan_json('BEGIN\n' + json.dumps(PLAN) + '\nROLLBACK'), PLAN)

    def test_transaction_and_timeout_commands_are_retained(self):
        commands = collector._build_explain_commands('SELECT 1;', True, 2)
        self.assertEqual(commands[0], 'BEGIN')
        self.assertEqual(commands[1], "SET LOCAL statement_timeout = '2000ms'")
        self.assertIn('ANALYZE, BUFFERS, FORMAT JSON', commands[2])
        self.assertEqual(commands[-1], 'ROLLBACK')


if __name__ == '__main__':
    unittest.main()
