"""Offline tests for DNS error handling, DKIM records, and DMARC advice."""

import base64
import importlib.util
import os
from pathlib import Path
import subprocess
import types
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_email_auth as cea  # noqa: E402


def run_dmarc(record, **kwargs):
    report = cea.DomainReport(domain="example.com", dns_backend="stub")
    with mock.patch.object(cea, "_query_txt", return_value=[record]):
        cea.check_dmarc("example.com", report, **kwargs)
    return report


def text(report, severity=None):
    return " ".join(f.message for f in report.findings if severity in (None, f.severity))


class TestParse(unittest.TestCase):
    def test_tags_are_split_and_lowercased(self):
        tags = cea.parse_dmarc_tags("v=DMARC1; P=quarantine; t=y; np=reject; rua=mailto:a@example.com")
        self.assertEqual(tags["p"], "quarantine")
        self.assertEqual(tags["t"], "y")
        self.assertEqual(tags["np"], "reject")


class TestStagedAdvice(unittest.TestCase):
    def test_none_without_reports_does_not_advise_tightening(self):
        # Without rua= there is no evidence; the advice must be to collect reports first.
        msg = text(run_dmarc("v=DMARC1; p=none"))
        self.assertIn("no evidence to tighten", msg)
        self.assertNotIn("Next stage", msg)

    def test_none_with_evidence_advances_one_stage_only(self):
        msg = text(run_dmarc("v=DMARC1; p=none; rua=mailto:r@example.com", sources_aligned=True))
        self.assertIn("Next stage: p=quarantine", msg)
        self.assertNotIn("Next stage: p=reject", msg)

    def test_quarantine_without_evidence_holds(self):
        msg = text(run_dmarc("v=DMARC1; p=quarantine; np=reject; rua=mailto:r@example.com"))
        self.assertIn("Hold here", msg)
        self.assertNotIn("Next stage: p=reject", msg)

    def test_quarantine_with_evidence_advances_to_reject(self):
        msg = text(run_dmarc("v=DMARC1; p=quarantine; np=reject; rua=mailto:r@example.com",
                             sources_aligned=True))
        self.assertIn("Next stage: p=reject", msg)

    def test_mailing_list_domain_stops_at_quarantine(self):
        msg = text(run_dmarc("v=DMARC1; p=quarantine; np=reject; rua=mailto:r@example.com",
                             sources_aligned=True, mailing_list_users=True))
        self.assertNotIn("Next stage: p=reject", msg)
        self.assertIn("SHOULD NOT", msg)
        warn = text(run_dmarc("v=DMARC1; p=reject; np=reject; rua=mailto:r@example.com",
                              mailing_list_users=True), "warning")
        self.assertIn("SHOULD NOT", warn)


class TestDmarcbisTags(unittest.TestCase):
    def test_t_y_is_reported_as_one_level_down(self):
        report = run_dmarc("v=DMARC1; p=quarantine; t=y; np=reject; rua=mailto:r@example.com")
        msg = text(report, "warning")
        self.assertIn("test mode", msg)
        self.assertIn("apply it as p=none", msg)
        self.assertNotIn("Full enforcement", text(report))

    def test_reject_t_y_applies_as_quarantine(self):
        msg = text(run_dmarc("v=DMARC1; p=reject; t=y; np=reject; rua=mailto:r@example.com"))
        self.assertIn("apply it as p=quarantine", msg)
        self.assertNotIn("Full enforcement", msg)

    def test_invalid_t_value_is_an_error(self):
        self.assertIn("t= value", text(run_dmarc("v=DMARC1; p=none; t=maybe; rua=mailto:r@example.com"), "error"))

    def test_np_none_under_enforcement_warns(self):
        msg = text(run_dmarc("v=DMARC1; p=reject; np=none; rua=mailto:r@example.com"), "warning")
        self.assertIn("np=none", msg)

    def test_np_falls_back_to_sp(self):
        msg = text(run_dmarc("v=DMARC1; p=reject; sp=none; rua=mailto:r@example.com"), "warning")
        self.assertIn("np= absent, so sp applies", msg)

    def test_pct_is_flagged_as_removed(self):
        msg = text(run_dmarc("v=DMARC1; p=quarantine; pct=50; np=reject; rua=mailto:r@example.com"), "warning")
        self.assertIn("removes pct", msg)

    def test_no_record_is_an_error(self):
        report = cea.DomainReport(domain="example.com", dns_backend="stub")
        with mock.patch.object(cea, "_query_txt", return_value=[]):
            cea.check_dmarc("example.com", report)
        self.assertTrue(report.errors)


class TestDkimFailClosed(unittest.TestCase):
    def report(self, records, selectors=None):
        report = cea.DomainReport(domain="example.com", dns_backend="stub")
        with mock.patch.object(cea, "_query_txt", return_value=records):
            cea.check_dkim("example.com", ["active"] if selectors is None else selectors, report)
        return report

    def test_empty_key_is_revoked(self):
        for record in ["v=DKIM1; k=rsa; p=", "v=DKIM1; k=rsa; p=; t=s"]:
            with self.subTest(record=record):
                self.assertTrue(self.report([record]).errors)

    def test_missing_key_cannot_pass(self):
        self.assertTrue(self.report(["v=DKIM1; k=rsa"]).errors)

    def test_duplicate_selector_keys_cannot_pass(self):
        key = "v=DKIM1; p=" + base64.b64encode(b"x" * 256).decode()
        self.assertTrue(self.report([key, key]).errors)

    def test_malformed_base64_cannot_pass(self):
        self.assertTrue(self.report(["v=DKIM1; p=" + "!" * 400]).errors)

    def test_unchecked_dkim_cannot_pass(self):
        self.assertTrue(self.report([], selectors=[]).errors)

    def test_missing_requested_selector_cannot_hide_behind_another(self):
        report = cea.DomainReport(domain="example.com", dns_backend="stub")
        key = "v=DKIM1; p=" + base64.b64encode(b"x" * 256).decode()
        with mock.patch.object(cea, "_query_txt", side_effect=[[key], []]):
            cea.check_dkim("example.com", ["first", "second"], report)
        self.assertTrue(report.errors)

    def test_valid_ed25519_uses_its_own_key_length(self):
        key = base64.b64encode(bytes(range(32))).decode()
        report = self.report([f"v=DKIM1; k=ed25519; p={key}"])
        self.assertFalse(report.errors)
        self.assertIn("dual-signing", text(report))

    def test_invalid_ed25519_length_cannot_pass(self):
        key = base64.b64encode(b"x" * 256).decode()
        self.assertTrue(self.report([f"v=DKIM1; k=ed25519; p={key}"]).errors)

    def test_unsupported_key_type_cannot_pass(self):
        key = base64.b64encode(b"x" * 256).decode()
        self.assertTrue(self.report([f"v=DKIM1; k=unknown; p={key}"]).errors)


class TestDnsBackend(unittest.TestCase):
    def load_backend(self, modules, suffix):
        path = Path(cea.__file__)
        name = f"email_auth_test_{suffix}"
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        with mock.patch.dict(sys.modules, {**modules, name: module}):
            spec.loader.exec_module(module)
        return module

    def test_dig_failure_cannot_be_treated_as_answer(self):
        module = self.load_backend({"dns": None, "dns.resolver": None, "dns.exception": None}, "dig")
        failed = subprocess.CompletedProcess([], 9, stdout='"v=DMARC1; p=reject"', stderr="failed")
        with mock.patch.object(module.subprocess, "run", return_value=failed):
            with self.assertRaises(LookupError):
                module._query_txt("example.com")

    def test_dnspython_concatenates_chunks_per_record(self):
        package = types.ModuleType("dns")
        resolver = types.ModuleType("dns.resolver")
        exception = types.ModuleType("dns.exception")
        class DnsError(Exception):
            pass
        exception.DNSException = DnsError
        for name in ["NXDOMAIN", "NoAnswer", "NoNameservers"]:
            setattr(resolver, name, type(name, (DnsError,), {}))
        resolver.resolve = mock.Mock(return_value=[types.SimpleNamespace(strings=(b"v=DKIM1; p=", b"YWJj"))])
        package.resolver, package.exception = resolver, exception
        module = self.load_backend({"dns": package, "dns.resolver": resolver, "dns.exception": exception}, "dns")
        self.assertEqual(module._query_txt("example.com"), ["v=DKIM1; p=YWJj"])
        resolver.resolve.side_effect = resolver.NoNameservers("SERVFAIL")
        with self.assertRaises(LookupError):
            module._query_txt("example.com")


if __name__ == "__main__":
    unittest.main()
