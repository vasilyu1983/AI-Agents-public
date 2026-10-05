"""Offline execution of the documented verifier with only external imports stubbed."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import unittest

SKILL = Path(__file__).resolve().parents[1]
TEMPLATE = Path(os.environ.get(
    "CRYPTO_TEMPLATE_PATH", str(SKILL / "assets/ethereum/template-solidity-hardhat.md")
))


@unittest.skipUnless(shutil.which("node"), "Node.js is needed to execute the verifier")
class VerificationTemplateTests(unittest.TestCase):
    def run_verifier(self, address=None, error=None):
        text = TEMPLATE.read_text()
        match = re.search(
            r"\*\*scripts/verify\.ts:\*\*\s*```typescript\n(.*?)\n```",
            text, re.DOTALL,
        )
        self.assertIsNotNone(match, "documented verification script is missing")
        script = re.sub(r"^import .*;\n", "", match.group(1), flags=re.MULTILINE)
        # The old template's catch annotation is the only TS-only syntax in this snippet.
        script = script.replace("error: any", "error")
        stub = """
const hre = {};
async function verifyContract() {
  if (process.env.TEST_VERIFY_ERROR) throw new Error(process.env.TEST_VERIFY_ERROR);
}
const run = verifyContract;
"""
        env = {k: v for k, v in os.environ.items()
               if k not in {"TOKEN_ADDRESS", "TEST_VERIFY_ERROR"}}
        if address is not None:
            env["TOKEN_ADDRESS"] = address
        if error is not None:
            env["TEST_VERIFY_ERROR"] = error
        return subprocess.run(
            ["node", "--input-type=module"], input=stub + script,
            text=True, capture_output=True, env=env, timeout=10,
        )

    def test_rejected_verification_is_nonzero(self):
        result = self.run_verifier("0x" + "1" * 40, "RPC rejected verification")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RPC rejected verification", result.stderr)
        self.assertNotIn("verified successfully", result.stdout.lower())

    def test_error_message_cannot_claim_already_verified_success(self):
        result = self.run_verifier("0x" + "1" * 40, "Already Verified but wrong chain")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Contract already verified", result.stdout)

    def test_missing_address_is_nonzero(self):
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("TOKEN_ADDRESS", result.stderr)

    def test_malformed_address_is_nonzero(self):
        result = self.run_verifier("0xnot-an-address")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("TOKEN_ADDRESS", result.stderr)

    def test_success_reports_success(self):
        result = self.run_verifier("0x" + "1" * 40)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Contract verified successfully", result.stdout)


if __name__ == "__main__":
    unittest.main()
