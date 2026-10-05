"""Offline wrapper regressions; the fake client models documented bypass settings."""
import os
import re
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(os.environ.get("PACT_GATE_UNDER_TEST", Path(__file__).with_name("pact_can_i_deploy.sh")))


class PactGateTests(unittest.TestCase):
    def test_unconfigured_ci_contract_step_blocks(self):
        asset = Path(os.environ.get("CONTRACT_MATRIX_UNDER_TEST", Path(__file__).resolve().parents[1] / "assets/schema-validation-matrix.md"))
        snippet = re.search(r"- name: Run executable contracts\n      run: \|\n(.*?)```", asset.read_text(), re.S).group(1)
        result = subprocess.run(["bash", "-c", snippet], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)

    def run_gate(self, overrides=None, result="failed"):
        with tempfile.TemporaryDirectory() as folder:
            fake = Path(folder) / "pact-broker"
            fake.write_text('''#!/usr/bin/env bash
# Model matrix_commands.rb: dry-run, omitted pairings, and exit override.
if [[ "${PACT_BROKER_CAN_I_DEPLOY_DRY_RUN:-}" == true || -n "${PACT_BROKER_CAN_I_DEPLOY_IGNORE:-}" || "${PACT_BROKER_CAN_I_DEPLOY_EXIT_CODE_BETA:-}" == 0 ]]; then
  exit 0
fi
[[ "${FAKE_RESULT}" == passed ]] && exit 0
exit 1
''')
            fake.chmod(0o755)
            env = {key: value for key, value in os.environ.items() if not key.startswith("PACT_BROKER_")}
            env.update(PATH=folder + os.pathsep + env.get("PATH", ""), PACT_BROKER_BASE_URL="https://broker.example.invalid", SERVICE="example-service", GIT_SHA="example-revision", FAKE_RESULT=result)
            env.update(overrides or {})
            return subprocess.run(["bash", str(SCRIPT)], env=env, text=True, capture_output=True)

    def test_success(self):
        result = self.run_gate(result="passed")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("is safe to deploy", result.stdout)

    def test_failed_verification_blocks(self):
        result = self.run_gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("is safe to deploy", result.stdout)

    def test_unknown_verification_blocks(self):
        result = self.run_gate(result="unknown")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("is safe to deploy", result.stdout)

    def test_dry_run_cannot_bypass(self):
        self.assert_override_blocks("PACT_BROKER_CAN_I_DEPLOY_DRY_RUN", "true")

    def test_ignored_pairing_cannot_bypass(self):
        self.assert_override_blocks("PACT_BROKER_CAN_I_DEPLOY_IGNORE", "example-consumer")

    def test_exit_override_cannot_bypass(self):
        self.assert_override_blocks("PACT_BROKER_CAN_I_DEPLOY_EXIT_CODE_BETA", "0")

    def assert_override_blocks(self, key, value):
        result = self.run_gate({key: value})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(key, result.stderr)
        self.assertNotIn("is safe to deploy", result.stdout)


if __name__ == "__main__":
    unittest.main()
