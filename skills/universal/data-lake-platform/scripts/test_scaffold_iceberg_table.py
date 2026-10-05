#!/usr/bin/env python3
"""Offline rejection tests for the Spark SQL DDL scaffold."""

from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).with_name("scaffold_iceberg_table.py")


class ScaffoldIcebergTest(unittest.TestCase):
    def test_rejects_sql_statement_boundaries_in_inputs(self):
        for name, columns in (
            ("analytics.events;DROP TABLE analytics.users", "id BIGINT"),
            ("analytics.events", "id BIGINT); DROP TABLE analytics.users; --"),
        ):
            with self.subTest(name=name, columns=columns):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), "--catalog", "rest", "--name", name,
                     "--columns", columns],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
