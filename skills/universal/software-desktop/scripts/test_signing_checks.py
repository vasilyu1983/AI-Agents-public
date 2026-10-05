#!/usr/bin/env python3
"""Offline signing regressions; mocked commands do not verify a real artifact."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(os.environ.get("SIGNING_SCRIPTS_DIR", Path(__file__).parent))


class ReadinessTests(unittest.TestCase):
    def run_config(self, value, *args):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.json"
            config.write_text(json.dumps(value))
            return subprocess.run(
                [sys.executable, str(SCRIPTS / "check_signing_readiness.py"), str(config), *args],
                capture_output=True, text=True,
            )

    def test_bad_shapes_fail_cleanly(self):
        for value in [[], {"platforms": [{}]}, {"platforms": ["macos"], "macos": []},
                      {"platforms": ["linux"], "linux": {"gpg_key_id": 7}},
                      {"platforms": ["windows"], "windows": {"signing_mode": []}},
                      {"platforms": ["windows"], "windows": {"signing_mode": {}}}]:
            with self.subTest(value=value):
                result = self.run_config(value)
                self.assertEqual(result.returncode, 1)
                self.assertNotIn("Traceback", result.stderr)

    def test_strict_missing_files_fail(self):
        result = self.run_config({"platforms": ["macos"], "macos": {
            "cert_path": "/nonexistent/signing-test.p12",
            "entitlements_file": "/nonexistent/signing-test.plist",
            "notarization_profile": "SYNTHETIC_PROFILE", "bundle_id": "com.example.app",
        }}, "--strict")
        self.assertEqual(result.returncode, 1)

    def test_store_route_accepts_msix_only(self):
        for package, expected in [("msix", 0), ("exe", 1)]:
            result = self.run_config({"platforms": ["windows"], "windows": {
                "signing_mode": "store", "package_type": package,
            }})
            self.assertEqual(result.returncode, expected)

    def test_nonempty_linux_config_passes(self):
        self.assertEqual(self.run_config({"platforms": ["linux"],
                                         "linux": {"gpg_key_id": "SYNTHETIC_ID"}}).returncode, 0)


class ArtifactTests(unittest.TestCase):
    def run_mock(self, *, os_name="Darwin", assessment_exit=0, assessment_source="Notarized Developer ID",
                 staple_exit=0, display_exit=0, extension="app"):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            target = base / ("Synthetic." + extension)
            target.mkdir()
            commands = {
                "uname": "#!/bin/sh\nprintf '%s\\n' \"$MOCK_OS\"\n",
                "codesign": """#!/bin/sh
if [ "$1" = "--display" ]; then
  printf '%s\\n' 'flags=0x10000(runtime)' 'TeamIdentifier=SYNTHETIC'
  exit "$MOCK_DISPLAY_EXIT"
fi
exit 0
""",
                "spctl": "#!/bin/sh\nprintf '%s\\n' accepted \"source=$MOCK_SOURCE\"\nexit \"$MOCK_ASSESS_EXIT\"\n",
                "xcrun": "#!/bin/sh\necho 'The validate action worked'\nexit \"$MOCK_STAPLE_EXIT\"\n",
            }
            for name, body in commands.items():
                path = base / name
                path.write_text(body)
                path.chmod(0o755)
            env = dict(os.environ, PATH=str(base) + os.pathsep + os.environ["PATH"],
                       MOCK_OS=os_name, MOCK_SOURCE=assessment_source,
                       MOCK_ASSESS_EXIT=str(assessment_exit), MOCK_STAPLE_EXIT=str(staple_exit),
                       MOCK_DISPLAY_EXIT=str(display_exit))
            return subprocess.run(["bash", str(SCRIPTS / "check_signing.sh"), str(target)],
                                  env=env, text=True, capture_output=True)

    def test_unsupported_os_does_not_pass(self):
        result = self.run_mock(os_name="Linux")
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("PASS:", result.stdout)

    def test_failed_assessment_with_accepted_text_fails(self):
        self.assertEqual(self.run_mock(assessment_exit=1).returncode, 1)

    def test_non_notarized_source_fails(self):
        self.assertEqual(self.run_mock(assessment_source="Developer ID").returncode, 1)

    def test_failed_staple_with_success_text_fails(self):
        self.assertEqual(self.run_mock(staple_exit=1).returncode, 1)

    def test_failed_metadata_command_fails(self):
        self.assertEqual(self.run_mock(display_exit=1).returncode, 1)

    def test_dmg_does_not_get_app_checks(self):
        self.assertEqual(self.run_mock(extension="dmg").returncode, 2)

    def test_mock_success_passes(self):
        self.assertEqual(self.run_mock().returncode, 0)


if __name__ == "__main__":
    unittest.main()
