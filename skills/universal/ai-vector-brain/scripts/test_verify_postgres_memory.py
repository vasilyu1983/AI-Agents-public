#!/usr/bin/env python3
"""Local runner controls; these never establish PostgreSQL correctness."""
import subprocess
import unittest
from unittest.mock import Mock
from verify_postgres_memory import build_sql, dsn_env, run


class RunnerControls(unittest.TestCase):
    def env(self):
        return {'MEMORY_TEST_ALLOW': 'dedicated-test-database', 'MEMORY_TEST_DSN': 'postgresql://private:secret@localhost/scratch', 'MEMORY_TEST_RLS_ROLE': 'memory_reader'}

    def test_requires_dedicated_database_acknowledgement(self):
        execute = Mock()
        code, result = run({}, execute=execute)
        self.assertEqual((code, result['status']), (2, 'not_run'))
        execute.assert_not_called()

    def test_missing_dsn_fails_closed(self):
        env = self.env(); del env['MEMORY_TEST_DSN']
        self.assertEqual(run(env)[0], 2)

    def test_missing_role_fails_closed(self):
        env = self.env(); del env['MEMORY_TEST_RLS_ROLE']
        self.assertEqual(run(env)[0], 2)

    def test_missing_psql_has_no_fake_fallback(self):
        self.assertEqual(run(self.env(), find_psql=lambda _: None)[1]['status'], 'not_run')

    def test_role_injection_rejected(self):
        env = self.env(); env['MEMORY_TEST_RLS_ROLE'] = 'reader"; DROP SCHEMA public CASCADE; --'
        execute = Mock()
        self.assertEqual(run(env, execute=execute)[0], 2)
        execute.assert_not_called()
        with self.assertRaises(ValueError):
            build_sql('scratch', env['MEMORY_TEST_RLS_ROLE'])

    def test_server_failure_and_credentials_not_echoed(self):
        execute = Mock(return_value=subprocess.CompletedProcess([], 1, '', 'secret DSN'))
        code, report = run(self.env(), find_psql=lambda _: '/usr/bin/psql', execute=execute)
        self.assertEqual((code, report['status']), (1, 'failed'))
        self.assertNotIn('secret', str(report))
        args, kwargs = execute.call_args
        self.assertNotIn('secret', str(args))
        # libpq never expands a URI held in PGDATABASE, so the runner must hand psql the parts
        self.assertEqual((kwargs['env']['PGDATABASE'], kwargs['env']['PGPASSWORD']), ('scratch', 'secret'))
        self.assertNotIn('MEMORY_TEST_DSN', kwargs['env'])
        self.assertTrue(kwargs['timeout'] > 0)

    def test_success_requires_completion_marker(self):
        execute = Mock(return_value=subprocess.CompletedProcess([], 0, '', ''))
        self.assertEqual(run(self.env(), find_psql=lambda _: 'psql', execute=execute)[0], 1)
        execute.return_value = subprocess.CompletedProcess([], 0, 'MEMORY_INTEGRATION_PASSED', '')
        self.assertEqual(run(self.env(), find_psql=lambda _: 'psql', execute=execute)[1]['status'], 'passed')

    def test_timeout_inconclusive(self):
        execute = Mock(side_effect=subprocess.TimeoutExpired('psql', 120))
        self.assertEqual(run(self.env(), find_psql=lambda _: 'psql', execute=execute)[1]['status'], 'inconclusive')

    def test_uri_split_into_libpq_variables(self):
        self.assertEqual(dsn_env('postgresql://app%40corp:p%3Ass@db.internal:6543/mem%20test?sslmode=verify-full&connect_timeout=5'),
                         {'PGUSER': 'app@corp', 'PGPASSWORD': 'p:ss', 'PGHOST': 'db.internal', 'PGPORT': '6543',
                          'PGDATABASE': 'mem test', 'PGSSLMODE': 'verify-full', 'PGCONNECT_TIMEOUT': '5'})
        self.assertEqual(dsn_env('postgres://h1:5432,[::1]:5433/db'),
                         {'PGHOST': 'h1,::1', 'PGPORT': '5432,5433', 'PGDATABASE': 'db'})
        self.assertEqual(dsn_env('postgresql:///scratch?host=/var/run/postgresql'),
                         {'PGDATABASE': 'scratch', 'PGHOST': '/var/run/postgresql'})

    def test_keyword_string_split_with_quoting(self):
        self.assertEqual(dsn_env("host=localhost  dbname = scratch password='it\\'s secret' sslmode=require"),
                         {'PGHOST': 'localhost', 'PGDATABASE': 'scratch', 'PGPASSWORD': "it's secret", 'PGSSLMODE': 'require'})

    def test_bare_database_name_unchanged(self):
        self.assertEqual(dsn_env('scratch'), {'PGDATABASE': 'scratch'})

    def test_unsupported_or_malformed_dsn_fails_closed_without_echo(self):
        for dsn in ('postgresql://u:secret@h/db?sslmod=require', "host=h password='secret", 'host=h secret',
                    'postgresql://u:secret@[::1/db', 'postgresql://u:secret@h/db?secret'):
            env = self.env(); env['MEMORY_TEST_DSN'] = dsn
            execute = Mock()
            code, report = run(env, find_psql=lambda _: 'psql', execute=execute)
            self.assertEqual((code, report['status']), (2, 'not_run'), dsn)
            self.assertNotIn('secret', str(report), dsn)
            execute.assert_not_called()

    def test_uri_plus_is_literal_and_encoded_space_is_space(self):
        self.assertEqual(dsn_env('postgresql://u:p+ass@h/db?password=a+b%20c&application_name=worker+one'),
                         {'PGUSER': 'u', 'PGPASSWORD': 'a+b c', 'PGHOST': 'h', 'PGDATABASE': 'db', 'PGAPPNAME': 'worker+one'})

    def test_unquoted_keyword_backslash_escapes(self):
        self.assertEqual(dsn_env(r"password=a\b dbname=my\ db host=local\host"),
                         {'PGPASSWORD': 'ab', 'PGDATABASE': 'my db', 'PGHOST': 'localhost'})
        self.assertEqual(dsn_env(r"password='a\\b' dbname=''"), {'PGPASSWORD': 'a\\b', 'PGDATABASE': ''})

    def test_bad_ipv6_suffix_and_empty_address_fail_before_subprocess(self):
        for authority in ('[::1]garbage', '[]', '[]:5432'):
            env = self.env(); env['MEMORY_TEST_DSN'] = 'postgresql://u:secret@' + authority + '/db'
            execute = Mock()
            code, report = run(env, find_psql=lambda _: 'psql', execute=execute)
            self.assertEqual((code, report['status']), (2, 'not_run'))
            self.assertNotIn('secret', str(report))
            execute.assert_not_called()

    def test_uri_invalid_percent_and_nul_fail_before_subprocess(self):
        for value in ('secret%', 'secret%2', 'secret%GG', 'secret%00', 'secret%ff', 'secret=other'):
            env = self.env(); env['MEMORY_TEST_DSN'] = 'postgresql://h/db?password=' + value
            execute = Mock()
            code, report = run(env, find_psql=lambda _: 'psql', execute=execute)
            self.assertEqual((code, report['status']), (2, 'not_run'))
            self.assertNotIn('secret', str(report))
            execute.assert_not_called()

    def test_missing_tenant_controls_run_against_populated_tables(self):
        # Construction guard for the former empty-table false-green, not backend evidence.
        sql = build_sql('memory_verify_test', 'memory_reader')
        missing = sql.index("'missing tenant denies'")
        for table in ('documents', 'chunks', 'embeddings'):
            seeded = sql.index(f"INSERT INTO {table} VALUES (1,'tenant:a'), (2,'tenant:b');")
            self.assertLess(seeded, missing)
            self.assertIn(f'NOT EXISTS(SELECT 1 FROM {table})', sql)
        self.assertLess(missing, sql.index("SELECT set_config('app.tenant_id','tenant:a',true)"))
        self.assertLess(sql.index('missing tenant write negative control accepted'), sql.index("SELECT set_config('app.tenant_id','tenant:a',true)"))
        self.assertIn("current_setting('app.tenant_id',true) IS NULL,'preflight missing tenant setting'", sql)
        self.assertGreater(sql.index("'empty tenant denies'"), sql.index("INSERT INTO documents VALUES (5,'tenant:b')"))

    def test_upgrade_drop_is_scratch_qualified(self):
        sql = build_sql('memory_verify_test', 'memory_reader')
        self.assertNotIn('DROP FUNCTION IF EXISTS assert_fact(', sql)
        self.assertIn('DROP FUNCTION IF EXISTS "memory_verify_test".assert_fact(', sql)
        self.assertIn('ROLLBACK;', sql)
        self.assertNotIn('COMMIT;\n\\echo', sql)


if __name__ == '__main__':
    unittest.main()
