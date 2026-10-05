"""Offline scaffold regression tests; run with python3 -m unittest discover."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(os.environ.get("IOS_AI_SCAFFOLD", Path(__file__).with_name("scaffold-composers.sh")))


class ScaffoldTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(["bash", str(SCRIPT), *map(str, args)], capture_output=True, text=True)

    def test_missing_target_fails(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage:", result.stderr)

    def test_preserves_existing_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            existing = Path(directory) / "GroundedAnswer.swift"
            existing.write_text("// app-owned source\n")
            self.assertEqual(self.run_script(directory).returncode, 0)
            self.assertEqual(existing.read_text(), "// app-owned source\n")
            self.assertTrue((Path(directory) / "ComposerChain.swift").is_file())
            before = {p.name: p.read_bytes() for p in Path(directory).glob("*.swift")}
            self.assertEqual(self.run_script(directory).returncode, 0)
            self.assertEqual(before, {p.name: p.read_bytes() for p in Path(directory).glob("*.swift")})

    @unittest.skipUnless(shutil.which("swiftc"), "Swift compiler unavailable")
    def test_unimplemented_validator_rejects_real_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(self.run_script(root).returncode, 0)
            main = root / "main.swift"
            main.write_text("""
import Foundation
let candidate = GroundedAnswer(
    answer: "Invented data must never pass an unimplemented validator.",
    grounding: "Unverified source", followUp: nil,
    archetype: .reflect, composerUsed: .sentenceBank,
    confidence: .high, anchorsNamed: [])
switch AnchorValidator().validate(candidate, bundle: EvidenceBundle()) {
case .failed: print("rejected")
case .ok: print("accepted")
}
""")
            executable = root / "validator-probe"
            result = subprocess.run(["swiftc", "-module-cache-path", str(root / "module-cache"), str(root / "GroundedAnswer.swift"),
                str(root / "EvidenceBundle.swift"), str(root / "AnchorValidator.swift"),
                str(main), "-o", str(executable)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([str(executable)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "rejected")


if __name__ == "__main__":
    unittest.main()
