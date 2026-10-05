#!/usr/bin/env python3
"""
test_citation_verifier.py — stdlib unittest for citation_verifier.py.

Covers the cases that were silently mis-scored "supported": fabricated
quote, negated quote, source unavailable — plus one genuinely correct
quote, so a naive always-fail rewrite cannot pass this suite either.
Also covers the SSRF guard on fetching (scheme allowlist, non-public
addresses, redirects, connected-peer re-check).

Run:
    python3 scripts/test_citation_verifier.py
"""

import http.server
import json
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import citation_verifier  # noqa: E402
from citation_verifier import (  # noqa: E402
    _check_connected_peer,
    _SafeRedirectHandler,
    build_safe_opener,
    fetch_source_text,
    url_is_safe_to_fetch,
    verify_entry,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "citation_verifier_cases.jsonl"


def load_case(ledger_id: str) -> dict:
    with FIXTURES.open(encoding="utf-8") as fh:
        for line in fh:
            entry = json.loads(line)
            if entry.get("ledger_id") == ledger_id:
                return entry
    raise KeyError(f"No fixture with ledger_id={ledger_id!r} in {FIXTURES}")


class TestCitationVerifier(unittest.TestCase):
    def test_fabricated_quote_is_not_supported(self):
        """A quote with the wrong number, not present in the source, must not pass."""
        entry = load_case("T1-fabricated")
        result = verify_entry(entry, strict=True)
        self.assertNotEqual(result["verdict"], "supported")
        self.assertEqual(result["verdict"], "unsupported")
        # The wrong figure is caught by the numeric check before the source
        # lookup; either reason is a correct rejection of this fixture.
        self.assertTrue("not found" in result["reason"].lower()
                        or "numeric mismatch" in result["reason"].lower(),
                        result["reason"])

    def test_negated_quote_is_not_supported(self):
        """A quote that negates the claim (source agrees with the negation) must not pass."""
        entry = load_case("T2-negated")
        result = verify_entry(entry, strict=True)
        self.assertNotEqual(result["verdict"], "supported")
        self.assertEqual(result["verdict"], "unsupported")
        self.assertIn("negat", result["reason"].lower())

    def test_correct_quote_is_supported(self):
        """A quote that is genuinely present and agrees with the claim should pass."""
        entry = load_case("T3-correct")
        result = verify_entry(entry, strict=True)
        self.assertEqual(result["verdict"], "supported")

    def test_source_unavailable_is_never_supported(self):
        """No source_text and an unreachable URL: must be 'unverified', never 'supported'."""
        entry = load_case("T4-source-unavailable")
        result = verify_entry(entry, strict=True, fetch=True)
        self.assertNotEqual(result["verdict"], "supported")
        self.assertEqual(result["verdict"], "unverified")

    def test_source_unavailable_with_fetch_disabled(self):
        """--no-fetch on an entry with a real quote and no source_text: still unverified."""
        entry = {
            "claim": "Water boils at 100 C at sea level.",
            "source_url": "https://example.com/facts",
            "supporting_quote": "Pure water boils at 100 degrees Celsius at sea level.",
        }
        result = verify_entry(entry, strict=True, fetch=False)
        self.assertEqual(result["verdict"], "unverified")


    def test_negated_quote_fails_even_without_source_text(self):
        """Negation contradicts the claim whatever the source says."""
        entry = {
            "claim": "Revenue grew 40 percent in 2025.",
            "source_url": "https://example.invalid/report",
            "supporting_quote": "Revenue did not grow 40 percent in 2025 at all.",
        }
        result = verify_entry(entry, strict=True, fetch=False)
        self.assertEqual(result["verdict"], "unsupported")

    def test_empty_claim_is_unsupported(self):
        """An empty claim has nothing to support; it must never be a soft 'needs_review'."""
        entry = dict(load_case("T3-correct"), claim="")
        result = verify_entry(entry, strict=True, fetch=False)
        self.assertEqual(result["verdict"], "unsupported")


TRANSFORMER_SOURCE = (
    "Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation "
    "task. On WMT 2014 English-to-French our big model achieves 41.8 BLEU. "
    "Training took 3.5 days on eight P100 GPUs. Revenue was up 12 percent year "
    "over year. The benchmark has 1,266 questions in total."
)


def _numeric_case(claim: str, quote: str) -> dict:
    """Quote is genuinely present in the source, so only the claim/quote number
    agreement decides the verdict."""
    return {
        "claim": claim,
        "source_url": "https://arxiv.org/abs/1706.03762",
        "supporting_quote": quote,
        "source_text": TRANSFORMER_SOURCE,
    }


class TestNumericAgreement(unittest.TestCase):
    """A quote that really is in the source must still carry the claim's figures.
    Before this check, a claim of 41.9 BLEU checked against a real quote saying
    28.4 BLEU came back 'supported'."""

    QUOTE_DE = "Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task"
    QUOTE_FR = "On WMT 2014 English-to-French our big model achieves 41.8 BLEU."

    def test_wrong_figure_in_claim_is_unsupported(self):
        r = verify_entry(_numeric_case(
            "The Transformer paper reports 41.9 BLEU on WMT 2014 English-to-German.",
            self.QUOTE_DE), strict=True, fetch=False)
        self.assertEqual(r["verdict"], "unsupported")
        self.assertIn("numeric mismatch", r["reason"].lower())
        self.assertIn("41.9", r["reason"])

    def test_near_miss_figure_is_unsupported(self):
        """41.9 vs 41.8: one tenth off is still a different number."""
        r = verify_entry(_numeric_case(
            "The big model reports 41.9 BLEU on English-to-French.", self.QUOTE_FR),
            strict=True, fetch=False)
        self.assertEqual(r["verdict"], "unsupported")

    def test_trailing_zero_is_the_same_number(self):
        """41.80 and 41.8 agree; the check must not reject formatting differences."""
        r = verify_entry(_numeric_case(
            "The big model reports 41.80 BLEU on English-to-French.", self.QUOTE_FR),
            strict=True, fetch=False)
        self.assertEqual(r["verdict"], "supported")

    def test_thousands_separator_is_the_same_number(self):
        r = verify_entry(_numeric_case(
            "The benchmark has 1266 questions.",
            "The benchmark has 1,266 questions in total."), strict=True, fetch=False)
        self.assertEqual(r["verdict"], "supported")

    def test_percent_sign_and_word_agree_but_values_must_match(self):
        ok = verify_entry(_numeric_case(
            "Revenue was up 12% year over year.",
            "Revenue was up 12 percent year over year."), strict=True, fetch=False)
        self.assertEqual(ok["verdict"], "supported")
        bad = verify_entry(_numeric_case(
            "Revenue was up 20% year over year.",
            "Revenue was up 12 percent year over year."), strict=True, fetch=False)
        self.assertEqual(bad["verdict"], "unsupported")
        self.assertIn("20", bad["reason"])
        self.assertNotIn("E+", bad["reason"])

    def test_claim_figure_absent_from_quote_is_unsupported(self):
        """The quote says 'eight' GPUs; a claim of 16 is not what the quote says."""
        r = verify_entry(_numeric_case(
            "Training took 3.5 days on 16 GPUs.",
            "Training took 3.5 days on eight P100 GPUs."), strict=True, fetch=False)
        self.assertEqual(r["verdict"], "unsupported")
        self.assertIn("16", r["reason"])

    def test_unit_mismatch_is_unsupported(self):
        r = verify_entry(_numeric_case(
            "Training took 3.5 hours on eight P100 GPUs.",
            "Training took 3.5 days on eight P100 GPUs."), strict=True, fetch=False)
        self.assertEqual(r["verdict"], "unsupported")
        self.assertIn("unit mismatch", r["reason"].lower())

    def test_numeric_mismatch_fails_even_when_source_unavailable(self):
        """A wrong figure is wrong regardless of whether the source could be fetched."""
        entry = _numeric_case("The Transformer paper reports 41.9 BLEU.", self.QUOTE_DE)
        del entry["source_text"]
        r = verify_entry(entry, strict=True, fetch=False)
        self.assertEqual(r["verdict"], "unsupported")

    def test_matching_figures_still_supported(self):
        """Positive control: the numeric check must not break the correct case."""
        r = verify_entry(_numeric_case(
            "The paper reports 28.4 BLEU on WMT 2014 English-to-German.",
            self.QUOTE_DE), strict=True, fetch=False)
        self.assertEqual(r["verdict"], "supported")


DRUG_SOURCE = (
    "Clinical summary. The drug is safe for adults only and is contraindicated "
    "in pregnancy. Dosing is limited to once daily. The label lists nausea as "
    "the most common side effect."
)


def _drug_case(claim: str, quote: str) -> dict:
    return {
        "claim": claim,
        "source_url": "https://example.com/label",
        "supporting_quote": quote,
        "source_text": DRUG_SOURCE,
    }


class TestContentAndQualifierGuard(unittest.TestCase):
    """The check is lexical, not entailment. Before this guard, a claim about
    children checked against a real quote saying 'adults only' came back
    'supported' because two of its three content words matched."""

    def test_claim_word_missing_from_quote_is_not_supported(self):
        r = verify_entry(_drug_case(
            "The drug is safe for children.",
            "The drug is safe for adults only"), strict=True, fetch=False)
        self.assertNotEqual(r["verdict"], "supported")
        self.assertEqual(r["verdict"], "needs_review")
        self.assertIn("children", r["reason"])

    def test_restricting_qualifier_in_quote_is_not_supported(self):
        """The quote narrows the claim ('limited to'); the claim drops the limit."""
        r = verify_entry(_drug_case(
            "Dosing is once daily.",
            "Dosing is limited to once daily"), strict=True, fetch=False)
        self.assertNotEqual(r["verdict"], "supported")
        self.assertEqual(r["verdict"], "needs_review")
        self.assertIn("limited", r["reason"])

    def test_qualifier_present_in_both_still_supported(self):
        """Positive control: a claim that keeps the quote's qualifier passes."""
        r = verify_entry(_drug_case(
            "The drug is safe for adults only.",
            "The drug is safe for adults only"), strict=True, fetch=False)
        self.assertEqual(r["verdict"], "supported")

    def test_reworded_attribution_still_supported(self):
        """Paraphrase the design does pass: attribution words ('paper',
        'reports') and number formatting may differ; content words may not."""
        r = verify_entry(_drug_case(
            "The label reports nausea as the most common side effect.",
            "The label lists nausea as the most common side effect."),
            strict=True, fetch=False)
        self.assertEqual(r["verdict"], "supported")

    def test_word_form_change_still_supported(self):
        """A change of word form ('lists' vs 'listed', 'common' vs 'commonest')
        is not a missing content word, or ordinary paraphrase never passes."""
        r = verify_entry(_drug_case(
            "The label listed nausea as the commonest side effect.",
            "The label lists nausea as the most common side effect."),
            strict=True, fetch=False)
        self.assertEqual(r["verdict"], "supported", r["reason"])

    def test_missing_word_fails_the_gate(self):
        entry = _drug_case("The drug is safe for children.",
                           "The drug is safe for adults only")
        self.assertEqual(_run_cli([entry], "--no-fetch"), 1)


SCRIPT = Path(__file__).resolve().parent / "citation_verifier.py"


def _run_cli(lines, *flags):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
        fh.write("".join(json.dumps(x) + "\n" for x in lines))
        path = fh.name
    try:
        return subprocess.run([sys.executable, str(SCRIPT), "--input", path, *flags],
                              capture_output=True, text=True).returncode
    finally:
        Path(path).unlink()


class TestCliGate(unittest.TestCase):
    """The exit code is the gate: it must fail closed."""

    def test_unverified_fails_by_default_and_passes_only_when_allowed(self):
        unverified = load_case("T4-source-unavailable")
        self.assertEqual(_run_cli([unverified], "--no-fetch"), 1)
        self.assertEqual(_run_cli([unverified], "--no-fetch", "--allow-unverified"), 0)

    def test_supported_only_passes(self):
        self.assertEqual(_run_cli([load_case("T3-correct")], "--no-fetch"), 0)

    def test_fabricated_fails_even_with_allow_unverified(self):
        self.assertEqual(_run_cli([load_case("T1-fabricated")], "--no-fetch", "--allow-unverified"), 1)

    def test_empty_input_fails(self):
        self.assertEqual(_run_cli([], "--no-fetch"), 2)

    def test_empty_claim_fails_the_gate(self):
        entry = dict(load_case("T3-correct"), claim="")
        self.assertEqual(_run_cli([entry], "--no-fetch", "--allow-unverified"), 1)

    def test_wrong_figure_fails_the_gate(self):
        entry = dict(load_case("T3-correct"),
                     claim="The Transformer paper reports 41.9 BLEU on WMT 2014 English-to-German.")
        self.assertEqual(_run_cli([entry], "--no-fetch", "--allow-unverified"), 1)

    def test_needs_review_fails_unless_allowed(self):
        """Low overlap is not a pass: exit 0 means every claim is supported."""
        entry = dict(load_case("T3-correct"),
                     claim="Attention mechanisms replace recurrence entirely in this architecture.")
        self.assertEqual(_run_cli([entry], "--no-fetch"), 1)
        self.assertEqual(_run_cli([entry], "--no-fetch", "--allow-needs-review"), 0)

    def test_non_object_json_line_is_an_input_error(self):
        """A JSON array or scalar on a line is exit 2 (cannot check), not a traceback."""
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
            fh.write("[1]\n")
            path = fh.name
        try:
            proc = subprocess.run([sys.executable, str(SCRIPT), "--input", path, "--no-fetch"],
                                  capture_output=True, text=True)
        finally:
            Path(path).unlink()
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertIn("not a JSON object", proc.stderr)


def _fake_getaddrinfo(ip_str: str):
    """Build a getaddrinfo()-shaped result resolving to a single fixed IP."""
    family = socket.AF_INET6 if ":" in ip_str else socket.AF_INET
    sockaddr = (ip_str, 443, 0, 0) if family == socket.AF_INET6 else (ip_str, 443)
    return [(family, socket.SOCK_STREAM, 6, "", sockaddr)]


class TestSsrfGuard(unittest.TestCase):
    """
    fetch_source_text must not reach local files or non-public hosts
    (arbitrary scheme, private DNS answers, redirects, DNS rebinding).
    DNS is mocked; the only real socket is a local test server.
    """

    def test_file_scheme_is_rejected(self):
        """file:// must be rejected on scheme alone, without doing any DNS lookup."""
        with mock.patch("citation_verifier.socket.getaddrinfo") as mock_dns:
            self.assertFalse(url_is_safe_to_fetch("file:///etc/passwd"))
            mock_dns.assert_not_called()

    def test_loopback_ip_is_rejected(self):
        """A hostname resolving to 127.0.0.1 must be blocked."""
        with mock.patch(
            "citation_verifier.socket.getaddrinfo",
            return_value=_fake_getaddrinfo("127.0.0.1"),
        ):
            self.assertFalse(url_is_safe_to_fetch("http://localhost.example/x"))

    def test_cloud_metadata_ip_is_rejected(self):
        """169.254.169.254 (cloud metadata endpoint) must be blocked as link-local."""
        with mock.patch(
            "citation_verifier.socket.getaddrinfo",
            return_value=_fake_getaddrinfo("169.254.169.254"),
        ):
            self.assertFalse(url_is_safe_to_fetch("http://metadata.example/latest"))

    def test_redirect_to_private_ip_is_blocked(self):
        """A 3xx redirect to a private IP must be rejected by the redirect handler."""
        handler = _SafeRedirectHandler()
        with mock.patch(
            "citation_verifier.socket.getaddrinfo",
            return_value=_fake_getaddrinfo("10.0.0.5"),
        ):
            with self.assertRaises(Exception):
                handler.redirect_request(
                    req=None, fp=None, code=302, msg="Found",
                    headers={}, newurl="http://internal.example/secret",
                )

    def test_public_address_passes_the_guard(self):
        """A hostname resolving only to a public IP is allowed through."""
        with mock.patch(
            "citation_verifier.socket.getaddrinfo",
            return_value=_fake_getaddrinfo("93.184.216.34"),
        ):
            self.assertTrue(url_is_safe_to_fetch("https://example.com/report"))

    def test_fetch_source_text_returns_none_when_blocked(self):
        """fetch_source_text must return None (never raise, never fetch) for a blocked URL."""
        with mock.patch("citation_verifier.socket.getaddrinfo") as mock_dns:
            result = fetch_source_text("file:///etc/passwd")
            self.assertIsNone(result)
            mock_dns.assert_not_called()

    def test_blocked_fetch_yields_unverified_verdict_never_supported(self):
        """End-to-end: a claim pointed at a metadata/loopback URL must verify as unverified."""
        entry = {
            "claim": "Internal config says debug mode is on.",
            "source_url": "http://169.254.169.254/latest/meta-data/",
            "supporting_quote": "debug mode is enabled for this instance",
        }
        with mock.patch(
            "citation_verifier.socket.getaddrinfo",
            return_value=_fake_getaddrinfo("169.254.169.254"),
        ):
            result = verify_entry(entry, strict=True, fetch=True)
        self.assertNotEqual(result["verdict"], "supported")
        self.assertEqual(result["verdict"], "unverified")

    def test_non_http_schemes_are_rejected(self):
        for url in ("ftp://example.com/x", "gopher://example.com/", "data:text/plain,hi",
                    "javascript:alert(1)", "//example.com/no-scheme"):
            with self.subTest(url=url):
                self.assertFalse(url_is_safe_to_fetch(url))

    def test_literal_private_and_loopback_hosts_are_rejected(self):
        """Literal IPs go through getaddrinfo unchanged; no mock needed."""
        for url in ("http://127.0.0.1/", "http://[::1]/", "http://10.1.2.3/",
                    "http://192.168.0.1/", "http://169.254.169.254/latest/",
                    "http://0.0.0.0/", "http://100.64.0.1/", "http://[fe80::1]/",
                    "http://[::ffff:127.0.0.1]/", "http://[::ffff:10.0.0.1]/"):
            with self.subTest(url=url):
                self.assertFalse(url_is_safe_to_fetch(url))

    def test_hostname_resolving_to_private_ip_is_rejected(self):
        with mock.patch(
            "citation_verifier.socket.getaddrinfo",
            return_value=_fake_getaddrinfo("10.0.0.5"),
        ):
            self.assertFalse(url_is_safe_to_fetch("https://intranet.example/doc"))

    def test_any_private_answer_among_several_is_rejected(self):
        answers = _fake_getaddrinfo("93.184.216.34") + _fake_getaddrinfo("192.168.1.10")
        with mock.patch("citation_verifier.socket.getaddrinfo", return_value=answers):
            self.assertFalse(url_is_safe_to_fetch("https://mixed.example/"))

    def test_dns_failure_fails_closed(self):
        with mock.patch("citation_verifier.socket.getaddrinfo",
                        side_effect=socket.gaierror("no such host")):
            self.assertFalse(url_is_safe_to_fetch("https://nowhere.example/"))

    def test_connected_peer_recheck_blocks_rebinding(self):
        """If DNS changed between pre-flight and connect, the peer check must still block."""
        sock = mock.Mock()
        sock.getpeername.return_value = ("127.0.0.1", 80)
        with self.assertRaises(OSError):
            _check_connected_peer(sock)
        sock.close.assert_called_once()
        sock.getpeername.return_value = ("93.184.216.34", 443)
        _check_connected_peer(sock)  # public peer: no exception

    def test_opener_has_no_file_or_ftp_handler(self):
        with self.assertRaises(urllib.error.URLError):
            build_safe_opener().open("file:///etc/passwd", timeout=1)


class _Handler(http.server.BaseHTTPRequestHandler):
    hits = []

    def do_GET(self):  # noqa: N802
        _Handler.hits.append(self.path)
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "http://internal.test/secret")
            self.end_headers()
        else:
            body = b"<html><body><p>Public page text for the verifier.</p></body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, *args):
        pass


def _can_bind_localhost() -> bool:
    """Sandboxes often forbid binding a port; skip the live-server test there."""
    try:
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
        return True
    except OSError:
        return False


@unittest.skipUnless(_can_bind_localhost(), "cannot bind a local port in this environment")
class TestRedirectEndToEnd(unittest.TestCase):
    """A real local server stands in for a 'public' host (127.0.0.1 is
    whitelisted for this test only); its redirect points at a host that
    resolves to a private address and must not be followed."""

    @classmethod
    def setUpClass(cls):
        cls.server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        _Handler.hits.clear()
        real_getaddrinfo = socket.getaddrinfo
        real_unsafe = citation_verifier._is_unsafe_ip

        def fake_getaddrinfo(host, *args, **kwargs):
            if host == "internal.test":
                return _fake_getaddrinfo("10.0.0.5")
            return real_getaddrinfo(host, *args, **kwargs)

        patches = [
            mock.patch("citation_verifier.socket.getaddrinfo", side_effect=fake_getaddrinfo),
            mock.patch("citation_verifier._is_unsafe_ip",
                       side_effect=lambda ip: False if ip == "127.0.0.1" else real_unsafe(ip)),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_positive_control_public_page_is_fetched(self):
        text = fetch_source_text(f"http://127.0.0.1:{self.port}/page", timeout=5)
        self.assertEqual(text, "Public page text for the verifier.")

    def test_redirect_to_private_host_is_not_followed(self):
        text = fetch_source_text(f"http://127.0.0.1:{self.port}/redirect", timeout=5)
        self.assertIsNone(text)
        self.assertEqual(_Handler.hits, ["/redirect"])


if __name__ == "__main__":
    unittest.main()
