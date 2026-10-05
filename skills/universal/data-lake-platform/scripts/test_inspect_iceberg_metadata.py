#!/usr/bin/env python3
"""Offline failure-path test for the Iceberg inventory helper."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("inspect_iceberg_metadata.sh")


class InspectMetadataTest(unittest.TestCase):
    def test_data_listing_failure_is_not_reported_as_zero_files(self):
        with tempfile.TemporaryDirectory() as directory:
            fake_aws = Path(directory, "aws")
            fake_aws.write_text(
                "#!/bin/sh\n"
                "if [ \"$1 $2 $3\" = 's3 ls s3://example/table/metadata/' ]; then\n"
                "  printf '2026-01-01 00:00:00 100 v1.metadata.json\\n2026-01-01 00:00:00 100 snap-1.avro\\n'\n"
                "elif [ \"$1 $2\" = 's3 cp' ]; then\n"
                "  printf '{\"format-version\":2,\"location\":\"s3://example/table\",\"snapshots\":[]}' > \"$4\"\n"
                "elif [ \"$1 $2\" = 's3 ls' ]; then\n"
                "  exit 42\n"
                "fi\n",
                encoding="utf-8",
            )
            fake_aws.chmod(0o755)
            result = subprocess.run(
                ["bash", str(SCRIPT), "--location", "s3://example/table", "--backend", "s3"],
                env={**os.environ, "PATH": f"{directory}:{os.environ['PATH']}"},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("data listing failed", result.stderr)
            self.assertNotIn("Total data files:      0", result.stdout)

    def test_gcs_backend_accepts_gs_uri_and_counts_objects(self):
        with tempfile.TemporaryDirectory() as directory:
            fake_gsutil = Path(directory, "gsutil")
            fake_gsutil.write_text(
                "#!/bin/sh\n"
                "if [ \"$1 $2\" = 'ls gs://example/table/metadata/' ]; then\n"
                "  printf 'gs://example/table/metadata/v1.metadata.json\\n'\n"
                "elif [ \"$1\" = 'cp' ]; then\n"
                "  printf '{\"format-version\":2,\"location\":\"gs://example/table\"}' > \"$4\"\n"
                "elif [ \"$1 $2\" = 'ls -r' ]; then\n"
                "  printf 'gs://example/table/data/part-1.parquet\\n'\n"
                "else\n"
                "  exit 42\n"
                "fi\n",
                encoding="utf-8",
            )
            fake_gsutil.chmod(0o755)
            result = subprocess.run(
                ["bash", str(SCRIPT), "--location", "gs://example/table", "--backend", "gcs"],
                env={**os.environ, "PATH": f"{directory}:{os.environ['PATH']}"},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Data files total          : 1", result.stdout)
            self.assertIn(".parquet                : 1", result.stdout)
            self.assertIn("Snapshots in candidate    : 0", result.stdout)
            self.assertIn("Candidate snapshot ID     : none", result.stdout)
            self.assertIn("Orphan candidates          : unverified", result.stdout)


if __name__ == "__main__":
    unittest.main()
