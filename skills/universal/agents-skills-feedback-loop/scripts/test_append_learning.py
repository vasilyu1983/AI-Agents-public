"""Regression coverage for append_learning.py, especially the redaction gate."""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "append_learning", Path(__file__).with_name("append_learning.py")
)
al = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(al)


class RedactionUnitTests(unittest.TestCase):
    def test_anthropic_api_key_redacted(self):
        text, tags = al.redact("use key sk-ant-api03-abcdefghijklmnopqrstuvwxyz for auth")
        self.assertNotIn("sk-ant-", text)
        self.assertIn("[REDACTED-API-KEY]", text)
        self.assertIn("[REDACTED-API-KEY]", tags)

    def test_generic_sk_key_redacted(self):
        text, _ = al.redact("openai key sk-abcdefghijklmnopqrstuvwxyz012345 leaked")
        self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz012345", text)
        self.assertIn("[REDACTED-API-KEY]", text)

    def test_github_pat_redacted(self):
        text, _ = al.redact("token ghp_abcdefghijklmnopqrstuvwxyzABCD in the log")
        self.assertNotIn("ghp_abcdefghijklmnopqrstuvwxyzABCD", text)
        self.assertIn("[REDACTED-API-KEY]", text)

    def test_aws_key_redacted(self):
        text, _ = al.redact("AWS key AKIAIOSFODNN7EXAMPLE was hardcoded")
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", text)
        self.assertIn("[REDACTED-AWS-KEY]", text)

    def test_bearer_token_redacted(self):
        text, _ = al.redact("send header Authorization: Bearer abc123def456ghi789 always")
        self.assertNotIn("abc123def456ghi789", text)
        self.assertIn("[REDACTED-BEARER-TOKEN]", text)

    def test_email_redacted(self):
        text, _ = al.redact("contact alice@example.com about the outage")
        self.assertNotIn("alice@example.com", text)
        self.assertIn("[REDACTED-EMAIL]", text)

    def test_home_path_redacted(self):
        text, _ = al.redact("path was /Users/alice/Documents/Code/project/skill")
        self.assertNotIn("alice", text)
        self.assertIn("/Users/[REDACTED-USER]", text)

    def test_linux_home_path_redacted(self):
        text, _ = al.redact("failed reading /home/alice/.config/thing.json")
        self.assertNotIn("alice", text)
        self.assertIn("/home/[REDACTED-USER]", text)

    def test_generic_high_entropy_token_redacted(self):
        text, tags = al.redact(
            "webhook secret whsec_8f3a9b2c7d1e4f6a0b9c8d7e6f5a4b3c2d1e0f9a leaked in logs"
        )
        self.assertIn("[REDACTED-TOKEN]", text)
        self.assertIn("[REDACTED-TOKEN]", tags)

    def test_clean_text_untouched(self):
        clean = "Webhook needs HMAC in the header, not the body."
        text, tags = al.redact(clean)
        self.assertEqual(text, clean)
        self.assertEqual(tags, [])

    def test_secret_after_key_name_redacted(self):
        # A17: a short secret is caught by its key name, not by its shape.
        text, tags = al.redact("set password=hunter2pass and token: abcdefgh12345 in the env")  # secret-scan: allow (fake test input)
        self.assertNotIn("hunter2pass", text)
        self.assertNotIn("abcdefgh12345", text)
        self.assertIn("password=[REDACTED-SECRET]", text)
        self.assertIn("token: [REDACTED-SECRET]", text)
        self.assertIn("[REDACTED-SECRET]", tags)

    def test_quoted_api_key_value_redacted(self):
        text, _ = al.redact('config had "api_key": "x9f3k2m8q1" committed')  # secret-scan: allow (fake test input)
        self.assertNotIn("x9f3k2m8q1", text)

    def test_dates_versions_prose_and_annotations_without_assignment_stay(self):
        clean = ("Fixed on 2026-10-03 in v1.2.3 (issue #1234); keep @Override and @Transactional; "
                 "the password is required and secret management needs review.")
        text, tags = al.redact(clean)
        self.assertEqual(text, clean)
        self.assertEqual(tags, [])

    def test_letters_only_and_symbol_secrets_after_key_redacted(self):
        # A letters-only or punctuated secret has no digit, so the shape rules miss it.
        for raw, secret in (("set password=hunterpass in prod", "hunterpass"),  # secret-scan: allow (fake test input)
                            ('"api_key": "abcdefghij" leaked', "abcdefghij"),  # secret-scan: allow (fake test input)
                            ("used passwd=P@ss!w0rd# once", "P@ss!w0rd#"),  # secret-scan: allow (fake test input)
                            ("token: Xk_Qwerty here", "Xk_Qwerty")):  # secret-scan: allow (fake test input)
            with self.subTest(raw=raw):
                text, tags = al.redact(raw)
                self.assertNotIn(secret, text)
                self.assertIn("[REDACTED-SECRET]", tags)

    def test_explicit_secret_assignments_redact_all_value_shapes(self):
        # Dates, words, and tiny numeric strings can all be real credentials.
        for value in ("1", "1234", "hunterpass", "2026-10-03", "v1.2.3", "required"):
            for template in ('password={}', 'password: {}', '"password": "{}"', "passwd='{}'"):
                with self.subTest(value=value, template=template):
                    text, tags = al.redact(template.format(value))
                    self.assertNotIn(value, text)
                    self.assertIn("[REDACTED-SECRET]", tags)

    def test_long_values_are_redacted_without_retaining_a_tail(self):
        for value in ("x" * 1024, "7" * 1024, "a0" * 512):
            for template in ('password={}', '"api_key": "{}"'):
                with self.subTest(template=template, value_type=value[:1]):
                    text, _ = al.redact(template.format(value))
                    self.assertNotIn(value[-16:], text)
                    self.assertLess(len(text), 80)

    def test_quoted_values_with_spaces_and_escaped_quotes_are_redacted(self):
        for raw in ('password="two secret words"', "passwd='two secret words'",
                    r'"api_key": "long\"secret tail"'):
            with self.subTest(raw=raw):
                text, tags = al.redact(raw)
                self.assertNotIn("secret", text)
                self.assertNotIn("tail", text)
                self.assertIn("[REDACTED-SECRET]", tags)

    def test_key_redaction_is_idempotent_and_preserves_existing_markers(self):
        for raw in ('password=1234', 'password: hunterpass', '"api_key": "two words"',  # secret-scan: allow (synthetic regression inputs)
                    'token: [REDACTED-API-KEY]', '"password": "[REDACTED-SECRET]"'):  # secret-scan: allow (redaction placeholders)
            with self.subTest(raw=raw):
                first, _ = al.redact(raw)
                second, tags = al.redact(first)
                self.assertEqual(second, first)
                self.assertEqual(tags, [])

    def test_unclosed_quoted_credentials_are_redacted_to_line_end(self):
        for raw in ('password="shortfake', "password='shortfake",
                    'password: "two fake words', "password: 'two fake words",
                    r'password="fake\"value', r"password='fake\'value",
                    'password="fake\\'):
            with self.subTest(raw=raw):
                text, tags = al.redact(raw)
                self.assertNotIn("fake", text)
                self.assertIn("[REDACTED-SECRET]", tags)
                self.assertEqual(al.redact(text), (text, []))

    def test_unclosed_quoted_credentials_do_not_consume_next_line(self):
        for quote in ('"', "'"):
            for newline in ("\n", "\r\n"):
                with self.subTest(quote=quote, newline=newline):
                    raw = "password=" + quote + "two fake words" + newline + "Keep this separate line."
                    text, tags = al.redact(raw)
                    self.assertNotIn("fake", text)
                    self.assertTrue(text.endswith(newline + "Keep this separate line."))
                    self.assertIn("[REDACTED-SECRET]", tags)
                    self.assertEqual(al.redact(text), (text, []))

    def test_assignment_redacts_vendor_and_bearer_suffixes(self):
        for raw in ("password=sk-" + "a" * 24 + "_tail123",  # secret-scan: allow (synthetic input)
                    "token=AKIA" + "A" * 16 + "tail123",  # secret-scan: allow (synthetic input)
                    "token=bearer " + "a" * 20 + "/tail123"):
            with self.subTest(raw=raw):
                text, tags = al.redact(raw)
                self.assertNotIn("tail123", text)
                self.assertIn("[REDACTED-SECRET]", tags)
                self.assertEqual(al.redact(text), (text, []))

    def test_only_complete_placeholder_values_are_preserved(self):
        raw = "password=[REDACTED-API-KEY]_tail123"  # secret-scan: allow (synthetic input)
        text, tags = al.redact(raw)
        self.assertEqual(text, "password=[REDACTED-SECRET]")
        self.assertIn("[REDACTED-SECRET]", tags)

    def test_plain_words_not_flagged_as_tokens(self):
        # No digits mixed with letters -> should not trip the generic
        # high-entropy catch-all.
        clean = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnop is not a secret"
        text, tags = al.redact(clean)
        self.assertEqual(text, clean)
        self.assertEqual(tags, [])


class AppendLearningCLITests(unittest.TestCase):
    """End-to-end: a secret passed on the CLI must never land on disk."""

    def _run(self, skill_dir: Path, text: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(Path(__file__).with_name("append_learning.py")),
                str(skill_dir),
                "--section",
                "Mistakes to Avoid",
                "--text",
                text,
                "--date",
                "2026-09-24",
            ],
            capture_output=True,
            text=True,
        )

    def test_secret_never_written_to_raw_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "sample-skill"
            skill_dir.mkdir()
            secret_key = "sk-ant-api03-FAKESECRETVALUEFORTESTONLY1234567890"
            result = self._run(skill_dir, f"Rotated the leaked key {secret_key} in prod")
            self.assertEqual(result.returncode, 0, result.stderr)
            raw_text = (skill_dir / "learnings.md").read_text()
            self.assertNotIn(secret_key, raw_text)
            self.assertIn("[REDACTED-API-KEY]", raw_text)
            # The CLI must have warned about the redaction on stderr.
            self.assertIn("redacted", result.stderr.lower())

    def test_short_and_long_assignment_secrets_never_written_to_raw_file(self):
        for secret in ("1234", "hunterpass", "x" * 1024):
            with self.subTest(secret_type=secret[:1]), tempfile.TemporaryDirectory() as tmp:
                skill_dir = Path(tmp) / "sample-skill"
                skill_dir.mkdir()
                result = self._run(skill_dir, f'Rotated password: "{secret}" after the leak.')  # secret-scan: allow (generated synthetic input)
                self.assertEqual(result.returncode, 0, result.stderr)
                raw_text = (skill_dir / "learnings.md").read_text()
                self.assertNotIn(secret, raw_text)
                self.assertIn("[REDACTED-SECRET]", raw_text)
                self.assertIn("redacted", result.stderr.lower())

    def test_email_never_written_to_raw_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "sample-skill"
            skill_dir.mkdir()
            result = self._run(skill_dir, "Escalate to alice@example.com when this recurs")
            self.assertEqual(result.returncode, 0, result.stderr)
            raw_text = (skill_dir / "learnings.md").read_text()
            self.assertNotIn("alice@example.com", raw_text)
            self.assertIn("[REDACTED-EMAIL]", raw_text)


if __name__ == "__main__":
    unittest.main()
