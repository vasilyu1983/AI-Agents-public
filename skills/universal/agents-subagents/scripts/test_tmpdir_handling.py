"""Deploy scripts must create temp files under TMPDIR, never a hardcoded /tmp.

On macOS a bare `mktemp` (no template) ignores TMPDIR and writes to the
per-user /var/folders path, and `mktemp "/tmp/..."` ignores TMPDIR by
construction. Both break in sandboxes that only allow writes under TMPDIR.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
DEPLOY_SCRIPTS = (SCRIPTS_DIR / "deploy-preset.sh", SCRIPTS_DIR / "deploy-all-teams.sh")

BARE_MKTEMP = re.compile(r"\$\(mktemp(?:\s+-d)?\)")
HARDCODED_TMP = re.compile(r"mktemp(?:\s+-d)?\s+\"?/tmp/")


class TmpdirHandlingTest(unittest.TestCase):
    def test_no_bare_or_hardcoded_mktemp(self) -> None:
        offenders: list[str] = []
        for script in DEPLOY_SCRIPTS:
            for lineno, line in enumerate(script.read_text().splitlines(), start=1):
                if BARE_MKTEMP.search(line) or HARDCODED_TMP.search(line):
                    offenders.append(f"{script.name}:{lineno}: {line.strip()}")
        self.assertEqual(offenders, [], "mktemp calls that ignore TMPDIR:\n" + "\n".join(offenders))

    def test_member_export_writes_under_tmpdir(self) -> None:
        """Source the Claude-to-Codex export function and confirm it lands in TMPDIR."""
        with tempfile.TemporaryDirectory() as tmp:
            script = (
                f"export TMPDIR={tmp!r}; "
                # Evaluate every mktemp call as the script would, without running the deploy.
                "grep -o 'mktemp[^)]*' \"$1\" | while read -r call; do "
                "  out=$(eval \"$call\" 2>&1) || { echo \"FAIL: $call -> $out\"; continue; }; "
                "  case \"$out\" in \"$TMPDIR\"/*|\"$META_DIR\"*) ;; *) echo \"OUTSIDE: $call -> $out\";; esac; "
                "done"
            )
            env = {"PATH": "/usr/bin:/bin", "META_DIR": tmp, "member_id": "x", "team_id": "t"}
            for path in DEPLOY_SCRIPTS:
                result = subprocess.run(
                    ["bash", "-c", script, "bash", str(path)],
                    text=True, capture_output=True, check=False, env=env, timeout=30,
                )
                self.assertEqual(
                    result.stdout.strip(), "", f"{path.name}: {result.stdout}{result.stderr}"
                )


if __name__ == "__main__":
    unittest.main()
