"""Offline runtime-proof regressions; no ADB device or Gradle process is used."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(os.environ.get("ANDROID_DESIGN_RUN_SCRIPT", Path(__file__).with_name("run-android.sh")))


class RunAndroidTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.apk_dir = self.root / "app/build/outputs/apk/debug"
        self.apk_dir.mkdir(parents=True)
        (self.apk_dir / "app.apk").touch()
        self.log = self.root / "adb.log"
        self.env = dict(os.environ, PATH=f"{self.bin}:/usr/bin:/bin", TEST_PROJECT=str(self.root),
                        TEST_LOG=str(self.log), TEST_ACTIVITY="com.example.app/.MainActivity",
                        TEST_LAUNCH="Status: ok")
        self.write_executable(self.root / "gradlew", "exit 0\n")
        self.write_executable(self.bin / "git", 'printf "%s\\n" "$TEST_PROJECT"\n')
        self.write_executable(self.bin / "adb", '''printf '%s\n' "$*" >> "$TEST_LOG"
case "$*" in
  "shell pm dump") echo 'com.unrelated.app' ;;
  *resolve-activity*) printf '%s\n' "$TEST_ACTIVITY" ;;
  *"am start"*) printf '%s\n' "$TEST_LAUNCH" ;;
  *) echo 'Success' ;;
esac
''')

    def write_executable(self, path, body):
        path.write_text("#!/bin/bash\n" + body)
        path.chmod(0o755)

    def run_script(self, *args):
        return subprocess.run(["/bin/bash", str(SCRIPT), *args], cwd=self.root,
                              env=self.env, capture_output=True, text=True, timeout=10)

    def adb_calls(self):
        return self.log.read_text() if self.log.exists() else ""

    def test_preserves_app_data_by_default(self):
        result = self.run_script("--package", "com.example.app")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("install -r", self.adb_calls())
        self.assertNotIn("uninstall", self.adb_calls())

    def test_package_must_come_from_artifact_or_argument(self):
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("install -r", self.adb_calls())
        self.assertNotIn("shell pm dump", self.adb_calls())

    def test_apk_badging_resolves_package(self):
        self.write_executable(self.bin / "aapt2", "echo \"package: name='com.example.app' versionCode='1'\"\n")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("com.example.app/.MainActivity", self.adb_calls())

    def test_unresolved_activity_fails(self):
        self.env["TEST_ACTIVITY"] = "No activity found"
        result = self.run_script("--package", "com.example.app")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("am start", self.adb_calls())

    def test_empty_activity_fails(self):
        self.env["TEST_ACTIVITY"] = ""
        self.assertNotEqual(self.run_script("--package", "com.example.app").returncode, 0)

    def test_other_package_activity_fails(self):
        self.env["TEST_ACTIVITY"] = "com.unrelated.app/.MainActivity"
        self.assertNotEqual(self.run_script("--package", "com.example.app").returncode, 0)
        self.assertNotIn("am start", self.adb_calls())

    def test_textual_launch_failure_fails_even_with_exit_zero(self):
        self.env["TEST_LAUNCH"] = "Error type 3\nError: Activity class does not exist."
        result = self.run_script("--package", "com.example.app")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("==> Done.", result.stdout)

    def test_ambiguous_apk_fails_before_install(self):
        (self.apk_dir / "split.apk").touch()
        self.assertNotEqual(self.run_script("--package", "com.example.app").returncode, 0)
        self.assertNotIn("install -r", self.adb_calls())

    def test_malformed_package_fails_before_install(self):
        self.assertNotEqual(self.run_script("--package", "not a package").returncode, 0)
        self.assertNotIn("install -r", self.adb_calls())


if __name__ == "__main__":
    unittest.main()
