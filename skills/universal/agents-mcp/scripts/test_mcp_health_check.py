"""Offline connection-gate regressions; never launch a configured MCP server."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(os.environ.get("MCP_HEALTH_SCRIPT", Path(__file__).with_name("mcp_health_check.sh")))

class ConnectionGateTests(unittest.TestCase):
    def run_gate(self, output, *args, code=0):
        with tempfile.TemporaryDirectory() as directory:
            stub = Path(directory) / "claude"
            stub.write_text('#!/bin/sh\nprintf "%s" "$MCP_FIXTURE"\nexit "$MCP_FIXTURE_EXIT"\n')
            stub.chmod(0o755)
            env = dict(os.environ, PATH=directory + os.pathsep + os.environ["PATH"],
                       MCP_FIXTURE=output, MCP_FIXTURE_EXIT=str(code))
            return subprocess.run(["/bin/bash", str(SCRIPT), *args], env=env,
                                  capture_output=True, text=True, timeout=10)

    def test_empty_inventory_fails(self):
        self.assertNotEqual(self.run_gate("").returncode, 0)

    def test_no_servers_message_fails(self):
        self.assertNotEqual(self.run_gate("No MCP servers configured.").returncode, 0)

    def test_connected_inventory_passes_without_claiming_tool_read(self):
        result = self.run_gate("Checking MCP server health...\nrepo: node server.js - ✓ Connected\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("read tool not checked", result.stdout)

    def test_failed_auth_disabled_and_unknown_status_fail(self):
        for status in ["! Needs authentication", "✘ Failed to connect: HTTP 500", "⏸ Pending approval",
                       "⊘ Disabled for this project", "cached 2h ago", "Connected"]:
            with self.subTest(status=status):
                self.assertNotEqual(self.run_gate(f"repo: endpoint - {status}\n").returncode, 0)

    def test_mixed_inventory_fails(self):
        self.assertNotEqual(self.run_gate("a: node a.js - ✓ Connected\nb: endpoint - ! Needs authentication\n").returncode, 0)

    def test_unrecognized_output_fails(self):
        self.assertNotEqual(self.run_gate("NAME TRANSPORT ENDPOINT\nrepo stdio /bin/sh").returncode, 0)

    def test_targeted_get_passes(self):
        result = self.run_gate("socket:\nType: ws\nStatus: ✔ Connected\n", "--server", "socket")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_target_or_status_fails(self):
        for output, code in [("No server found", 1), ("repo:\nCommand: node", 0),
                             ("Status: ✓ Connected\nStatus: ✘ Failed to connect", 0)]:
            with self.subTest(output=output):
                self.assertNotEqual(self.run_gate(output, "--server", "repo", code=code).returncode, 0)

    def test_cli_error_fails_without_echoing_sensitive_output(self):
        result = self.run_gate("synthetic-secret-token", code=1)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("synthetic-secret-token", result.stdout + result.stderr)

    def test_verbose_does_not_echo_endpoint_or_server_response(self):
        result = self.run_gate("repo: https://example.invalid/?token=synthetic-secret-token - ✓ Connected\n", "--verbose")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("synthetic-secret-token", result.stdout + result.stderr)

    def test_ansi_status_passes(self):
        result = self.run_gate("repo: command - \x1b[32m✓ Connected\x1b[0m\n")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_duplicate_names_fail(self):
        self.assertNotEqual(self.run_gate("repo: a - ✓ Connected\nrepo: b - ✓ Connected\n").returncode, 0)

    def test_invalid_options_fail(self):
        for args in [("--server",), ("--server", ""), ("--unknown",)]:
            with self.subTest(args=args):
                self.assertNotEqual(self.run_gate("", *args).returncode, 0)

if __name__ == "__main__":
    unittest.main()
