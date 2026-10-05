#!/usr/bin/env python3
"""
check_email_auth.py — Query DNS records for a domain and report SPF, DKIM, DMARC, and BIMI gaps.

Usage:
    python3 check_email_auth.py <domain> [--dkim-selectors SELECTOR [SELECTOR ...]] [--verbose]
    python3 check_email_auth.py --help

Requirements:
    - dnspython (pip install dnspython) — preferred for reliable DNS resolution
    - Falls back to subprocess dig if dnspython is not installed

Exit codes:
    0 — no errors (warnings are informational only)
    1 — one or more authentication gaps found (error-level findings)

Examples:
    python3 check_email_auth.py example.com
    python3 check_email_auth.py example.com --dkim-selectors default google s1 s2
    python3 check_email_auth.py example.com --verbose
    python3 check_email_auth.py example.com --all-sources-aligned   # after reviewing aggregate reports
"""

from __future__ import annotations

import argparse
import base64
import binascii
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# DNS backend — prefer dnspython, fall back to dig
# ---------------------------------------------------------------------------

try:
    import dns.resolver  # type: ignore
    import dns.exception  # type: ignore

    _DNS_BACKEND = "dnspython"

    def _query_txt(name: str) -> list[str]:
        """Return a list of TXT record strings for the given DNS name."""
        try:
            answers = dns.resolver.resolve(name, "TXT", lifetime=10)
            results = []
            for rdata in answers:
                results.append(b"".join(rdata.strings).decode("utf-8", errors="replace"))
            return results
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return []
        except dns.exception.DNSException as exc:
            raise LookupError(f"DNS error querying {name}: {exc}") from exc

except ImportError:
    _DNS_BACKEND = "dig"

    def _query_txt(name: str) -> list[str]:  # type: ignore[misc]
        """Return a list of TXT record strings using dig as a subprocess fallback."""
        try:
            result = subprocess.run(
                ["dig", "+short", "TXT", name],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except FileNotFoundError:
            raise LookupError("dig is not available and dnspython is not installed. "
                              "Install dnspython: pip install dnspython") from None
        except subprocess.TimeoutExpired:
            raise LookupError(f"dig timed out querying {name}") from None

        if result.returncode != 0:
            raise LookupError(f"dig failed querying {name} (exit {result.returncode})")

        lines = []
        for line in result.stdout.splitlines():
            line = line.strip().strip('"')
            # dig sometimes returns multi-part TXT as multiple quoted strings on one line
            # Concatenate quoted parts: "v=spf1" " include:..." -> "v=spf1 include:..."
            # Simple approach: remove quote characters and collapse
            combined = re.sub(r'"\s+"', "", line).replace('"', "")
            if combined:
                lines.append(combined)
        return lines


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    severity: str  # "error" | "warning" | "info"
    check: str
    message: str
    record: Optional[str] = None


@dataclass
class DomainReport:
    domain: str
    dns_backend: str
    findings: list[Finding] = field(default_factory=list)

    def add(self, severity: str, check: str, message: str, record: Optional[str] = None) -> None:
        self.findings.append(Finding(severity=severity, check=check, message=message, record=record))

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warning"]

    @property
    def infos(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "info"]


# ---------------------------------------------------------------------------
# SPF check
# ---------------------------------------------------------------------------

def check_spf(domain: str, report: DomainReport) -> None:
    try:
        records = _query_txt(domain)
    except LookupError as exc:
        report.add("error", "SPF", f"DNS lookup failed: {exc}")
        return

    spf_records = [r for r in records if r.startswith("v=spf1")]

    if not spf_records:
        report.add(
            "error", "SPF",
            f"No SPF record found for {domain}. "
            "Add a DNS TXT record: v=spf1 include:<esp-domain> ~all",
        )
        return

    if len(spf_records) > 1:
        report.add(
            "error", "SPF",
            f"Multiple SPF records found for {domain} — only one is valid per RFC 7208. "
            "Having multiple SPF records causes SPF to fail.",
            record=str(spf_records),
        )
        return

    spf = spf_records[0]

    # Soft-fail vs hard-fail
    if spf.endswith("-all"):
        report.add("info", "SPF", f"SPF record uses -all (hard fail). Good.", record=spf)
    elif spf.endswith("~all"):
        report.add("info", "SPF", f"SPF record uses ~all (soft fail). Consider -all for stricter enforcement.", record=spf)
    elif spf.endswith("+all"):
        report.add(
            "error", "SPF",
            "+all authorizes any server to send on your behalf — this makes SPF useless. "
            "Change to ~all or -all.",
            record=spf,
        )
    else:
        report.add("warning", "SPF", f"SPF record does not end with 'all' mechanism — verify it is complete.", record=spf)

    # DNS lookup count (rudimentary: count include: and redirect= mechanisms)
    lookup_count = len(re.findall(r"\b(?:include:|redirect=|a:|mx:)", spf))
    if lookup_count > 9:
        report.add(
            "error", "SPF",
            f"SPF record has approximately {lookup_count} DNS-lookup mechanisms. "
            "RFC 7208 limits total DNS lookups to 10; exceeding this causes SPF to PermError.",
            record=spf,
        )
    elif lookup_count > 7:
        report.add(
            "warning", "SPF",
            f"SPF record has approximately {lookup_count} DNS-lookup mechanisms — approaching the 10-lookup limit.",
            record=spf,
        )


# ---------------------------------------------------------------------------
# DKIM check
# ---------------------------------------------------------------------------

def check_dkim(domain: str, selectors: list[str], report: DomainReport) -> None:
    if not selectors:
        report.add(
            "error", "DKIM",
            "No DKIM selectors provided. Cannot verify DKIM without knowing the selector. "
            "Pass --dkim-selectors to check specific selectors (e.g. default, google, s1, s2).",
        )
        return

    found_any = False

    for selector in selectors:
        dkim_name = f"{selector}._domainkey.{domain}"
        try:
            records = _query_txt(dkim_name)
        except LookupError as exc:
            report.add("error", "DKIM", f"DNS lookup failed for {dkim_name}: {exc}")
            continue

        dkim_records = [r for r in records if "v=DKIM1" in r or "k=rsa" in r or "k=ed25519" in r or "p=" in r]

        if not dkim_records:
            report.add(
                "error", "DKIM",
                f"No DKIM record found at {dkim_name}. "
                "If this selector is active, add the TXT record provided by your ESP.",
            )
            continue

        found_any = True
        if len(dkim_records) != 1:
            report.add("error", "DKIM", f"Multiple DKIM key records at {dkim_name}; selector is invalid.")
            continue
        dkim = dkim_records[0]
        report.add("info", "DKIM", f"DKIM record found at {dkim_name}.", record=dkim[:120])
        tags = parse_dmarc_tags(dkim)
        if "p" not in tags:
            report.add("error", "DKIM", f"DKIM key at {dkim_name} is missing required p= key material.")
            continue
        p_value = "".join(tags["p"].split())
        if not p_value:
            report.add("error", "DKIM", f"DKIM key at {dkim_name} has an empty p= value — this revokes the key.")
            continue
        try:
            key = base64.b64decode(p_value, validate=True)
        except (ValueError, binascii.Error):
            report.add("error", "DKIM", f"DKIM p= at {dkim_name} is not valid base64.")
            continue
        key_type = tags.get("k", "rsa").lower()
        if key_type == "ed25519":
            if len(key) != 32:
                report.add("error", "DKIM", f"Ed25519 public key at {dkim_name} must decode to 32 bytes.")
            else:
                report.add("warning", "DKIM", "Ed25519 record found; verify RSA dual-signing and recipient support.")
        elif key_type != "rsa":
            report.add("error", "DKIM", f"Unsupported DKIM key type '{key_type}' at {dkim_name}.")
        else:
            # DER overhead means base64 length is not the RSA modulus size.
            report.add("warning", "DKIM", "RSA key material found. Inspect the decoded public key with a "
                       "cryptographic tool to confirm modulus size; RFC 8301 requires at least 1024 bits "
                       "and recommends at least 2048 bits. DNS presence does not verify a message signature.")

    if not found_any and selectors:
        report.add(
            "error", "DKIM",
            f"No DKIM records found for any of the provided selectors ({selectors}) on {domain}. "
            "DKIM is required for Google/Yahoo bulk-sender compliance. "
            "Configure DKIM signing in your ESP and add the TXT record.",
        )


# ---------------------------------------------------------------------------
# DMARC check
# ---------------------------------------------------------------------------

def parse_dmarc_tags(record: str) -> dict[str, str]:
    """Split a DMARC record into a lower-cased tag -> value map."""
    tags: dict[str, str] = {}
    for part in record.split(";"):
        if "=" not in part:
            continue
        key, _, value = part.partition("=")
        key = key.strip().lower()
        if key and key not in tags:
            tags[key] = value.strip()
    return tags


_VALID_POLICIES = {"none", "quarantine", "reject"}


def check_dmarc(
    domain: str,
    report: DomainReport,
    sources_aligned: bool = False,
    mailing_list_users: bool = False,
) -> None:
    """Check DMARC and recommend the *next* stage only, never a jump to reject.

    The staged path is p=none (collect aggregate reports) -> p=quarantine
    (optionally t=y first) -> p=reject. DNS alone cannot show whether every
    legitimate sender aligns; that evidence comes from aggregate reports, so
    the caller states it with sources_aligned. Without it, the advice is to
    hold the current stage and review reports. Domains whose users post to
    mailing lists should stop at quarantine (DMARCbis says SHOULD NOT reject).
    """
    dmarc_name = f"_dmarc.{domain}"
    try:
        records = _query_txt(dmarc_name)
    except LookupError as exc:
        report.add("error", "DMARC", f"DNS lookup failed for {dmarc_name}: {exc}")
        return

    dmarc_records = [r for r in records if r.startswith("v=DMARC1")]

    if not dmarc_records:
        report.add(
            "error", "DMARC",
            f"No DMARC record found at {dmarc_name}. "
            "DMARC is required for Google/Yahoo bulk-sender compliance. "
            "Start with: v=DMARC1; p=none; rua=mailto:dmarc-reports@yourdomain.com",
        )
        return

    if len(dmarc_records) > 1:
        report.add(
            "error", "DMARC",
            f"Multiple DMARC records found at {dmarc_name}. Only one is valid.",
            record=str(dmarc_records),
        )
        return

    dmarc = dmarc_records[0]
    tags = parse_dmarc_tags(dmarc)
    report.add("info", "DMARC", "DMARC record found.", record=dmarc)

    has_rua = bool(tags.get("rua"))
    if not has_rua:
        report.add(
            "warning", "DMARC",
            "DMARC record is missing rua= aggregate report destination. "
            "Without aggregate reports, you cannot identify misauthenticated sending sources "
            "or decide when to tighten the policy. "
            "Add rua=mailto:dmarc-reports@yourdomain.com or a DMARC reporting service address.",
        )

    # t= (DMARCbis test mode): t=y asks receivers to apply the policy one level down.
    t_value = tags.get("t", "n").lower()
    testing = t_value == "y"
    if t_value not in {"y", "n"}:
        report.add("error", "DMARC", f"DMARC t= value '{t_value}' is not valid. Must be y or n.", record=dmarc)

    if "pct" in tags:
        report.add(
            "warning", "DMARC",
            f"DMARC record uses pct={tags['pct']}. DMARCbis removes pct; use t=y for a trial stage instead.",
            record=dmarc,
        )

    p = tags.get("p", "").lower()
    if not p:
        report.add("error", "DMARC", "DMARC record is missing the required p= policy tag.", record=dmarc)
    elif p not in _VALID_POLICIES:
        report.add("error", "DMARC", f"DMARC p= value '{p}' is not valid. Must be none, quarantine, or reject.", record=dmarc)
    else:
        _recommend_next_stage(p, testing, has_rua, sources_aligned, mailing_list_users, dmarc, report)

    # sp= existing subdomains, np= non-existent subdomains (np falls back to sp, then p).
    sp = tags.get("sp", "").lower()
    if sp and sp not in _VALID_POLICIES:
        report.add("error", "DMARC", f"DMARC sp= value '{sp}' is not valid.", record=dmarc)
    elif sp == "none" and p in {"quarantine", "reject"}:
        report.add(
            "warning", "DMARC",
            "DMARC sp=none leaves existing subdomains unprotected even though the root policy is enforcing. "
            "Raise sp= once subdomain senders appear aligned in aggregate reports.",
        )

    np_value = tags.get("np", "").lower()
    effective_np = np_value or sp or p
    if np_value and np_value not in _VALID_POLICIES:
        report.add("error", "DMARC", f"DMARC np= value '{np_value}' is not valid.", record=dmarc)
    elif effective_np == "none" and p in {"quarantine", "reject"}:
        source = "np=none" if np_value else "sp=none (np= absent, so sp applies)"
        report.add(
            "warning", "DMARC",
            f"Non-existent subdomains are unprotected ({source}). Nothing legitimate sends from a "
            "subdomain that does not exist, so np=reject is safe to publish.",
        )
    elif not np_value:
        report.add(
            "info", "DMARC",
            f"No np= tag; non-existent subdomains fall back to {'sp' if sp else 'p'}={effective_np}. "
            "np=reject protects them without affecting real senders.",
        )


def _recommend_next_stage(
    p: str,
    testing: bool,
    has_rua: bool,
    sources_aligned: bool,
    mailing_list_users: bool,
    record: str,
    report: DomainReport,
) -> None:
    applied = {"none": "none", "quarantine": "none", "reject": "quarantine"}[p] if testing else p
    stage = f"p={p}" + ("; t=y" if testing else "")
    if testing:
        report.add(
            "warning", "DMARC",
            f"DMARC is in test mode ({stage}); receivers apply it as p={applied}. "
            + ("Drop t=y once aggregate reports show every legitimate source aligned."
               if sources_aligned else "Keep t=y until aggregate reports show every legitimate source aligned."),
            record=record,
        )
        return

    if p == "none":
        if not has_rua:
            msg = ("DMARC policy is p=none with no rua= reports, so there is no evidence to tighten on. "
                   "Add rua= and review aggregate reports before moving to p=quarantine.")
        elif sources_aligned:
            msg = ("DMARC policy is p=none and you report every legitimate source aligned. "
                   "Next stage: p=quarantine (optionally with t=y first), not a jump to p=reject.")
        else:
            msg = ("DMARC policy is p=none: monitoring only, with no spoofing protection. "
                   "Review aggregate reports until every legitimate source aligns, then move to p=quarantine "
                   "(re-run with --all-sources-aligned once the reports show it).")
        report.add("warning", "DMARC", msg, record=record)
    elif p == "quarantine":
        if mailing_list_users:
            report.add(
                "info", "DMARC",
                "DMARC policy is p=quarantine. This domain's users post to mailing lists, and DMARCbis says "
                "such domains SHOULD NOT publish p=reject; quarantine is the recommended end state.",
            )
        elif sources_aligned and has_rua:
            report.add(
                "info", "DMARC",
                "DMARC policy is p=quarantine and you report every legitimate source aligned. "
                "Next stage: p=reject.",
            )
        else:
            report.add(
                "info", "DMARC",
                "DMARC policy is p=quarantine. Hold here until aggregate reports show every legitimate "
                "source aligned, then consider p=reject.",
            )
    else:  # reject
        if mailing_list_users:
            report.add(
                "warning", "DMARC",
                "DMARC policy is p=reject on a domain whose users post to mailing lists; DMARCbis says "
                "such domains SHOULD NOT publish p=reject. Expect list mail to be rejected, or step back to p=quarantine.",
                record=record,
            )
        else:
            report.add("info", "DMARC", "DMARC policy is p=reject. Full enforcement.")


# ---------------------------------------------------------------------------
# BIMI check
# ---------------------------------------------------------------------------

def check_bimi(domain: str, report: DomainReport) -> None:
    bimi_name = f"default._bimi.{domain}"
    try:
        records = _query_txt(bimi_name)
    except LookupError as exc:
        report.add("info", "BIMI", f"DNS lookup failed for {bimi_name}: {exc}")
        return

    bimi_records = [r for r in records if "v=BIMI1" in r]

    if not bimi_records:
        report.add(
            "info", "BIMI",
            f"No BIMI record found at {bimi_name}. "
            "BIMI is optional but displays your brand logo in supporting email clients (Gmail, Yahoo). "
            "Requires enforcing DMARC; certificate requirements depend on the target mailbox provider.",
        )
        return

    bimi = bimi_records[0]
    report.add("info", "BIMI", "BIMI record found.", record=bimi)

    # Check for VMC (a= tag)
    bimi_tags = parse_dmarc_tags(bimi)
    if not bimi_tags.get("a") or not bimi_tags["a"].startswith("https://"):
        report.add(
            "warning", "BIMI",
            "BIMI record has no usable HTTPS a= certificate URL. "
            "Verify the target mailbox provider\'s accepted certificate type and issuer before deployment.",
            record=bimi,
        )

    # Check for logo URL (l= tag)
    l_match = re.search(r"\bl=([^;]+)", bimi)
    if not l_match or not l_match.group(1).strip():
        report.add(
            "error", "BIMI",
            "BIMI record is missing the l= (logo URL) tag or it is empty.",
            record=bimi,
        )
    else:
        logo_url = l_match.group(1).strip()
        if not logo_url.startswith("https://"):
            report.add(
                "error", "BIMI",
                f"BIMI logo URL must use HTTPS: {logo_url}",
                record=bimi,
            )


# ---------------------------------------------------------------------------
# Report printer
# ---------------------------------------------------------------------------

def print_report(report: DomainReport, verbose: bool) -> int:
    errors = report.errors
    warnings = report.warnings
    infos = report.infos

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")

    print(f"## Email Authentication Report — {report.domain}")
    print(f"   DNS backend : {report.dns_backend}")
    print(f"   Status      : {status}")
    print(f"   Errors      : {len(errors)}")
    print(f"   Warnings    : {len(warnings)}")
    print(f"   Info        : {len(infos)}")
    print()

    if errors:
        print("### Errors (authentication gaps — action required)")
        for f in errors:
            print(f"  [{f.check}] {f.message}")
            if f.record:
                print(f"          Record: {f.record}")
            print()

    if warnings:
        print("### Warnings (recommended improvements)")
        for f in warnings:
            print(f"  [{f.check}] {f.message}")
            if f.record:
                print(f"          Record: {f.record}")
            print()

    if verbose and infos:
        print("### Info (DNS observations)")
        for f in infos:
            print(f"  [{f.check}] {f.message}")
            if f.record:
                print(f"          Record: {f.record}")
            print()

    return 1 if errors else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Query DNS records for a domain and report SPF, DKIM, DMARC, and BIMI gaps. "
            "Uses dnspython if installed, falls back to dig subprocess."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Checks performed:
  SPF     Presence, -all vs ~all, multiple record conflict, DNS lookup count
  DKIM    Required selectors, missing/revoked/malformed key, Ed25519 length; RSA size needs external inspection
  DMARC   Presence, staged p= advice (none -> quarantine -> reject), t= test mode,
          rua= reports, sp=/np= subdomain policies, removed pct=
  BIMI    Optional: presence, VMC (a= tag), logo URL (l= tag)

Examples:
  python3 check_email_auth.py example.com
  python3 check_email_auth.py example.com --dkim-selectors default google s1 s2
  python3 check_email_auth.py example.com --dkim-selectors resend1 --verbose

Install dnspython for reliable DNS resolution:
  pip install dnspython
""",
    )
    parser.add_argument("domain", help="Domain to check (e.g. example.com)")
    parser.add_argument(
        "--dkim-selectors", "-s",
        nargs="+",
        default=[],
        metavar="SELECTOR",
        help="DKIM selector names to check (e.g. default google s1 resend1). "
             "DKIM cannot be checked without knowing the selector.",
    )
    parser.add_argument(
        "--all-sources-aligned",
        action="store_true",
        help="State that DMARC aggregate reports show every legitimate sending source passing "
             "alignment. DNS cannot show this; without it the DMARC advice is to hold the current stage.",
    )
    parser.add_argument(
        "--mailing-list-users",
        action="store_true",
        help="The domain hosts users who post to mailing lists; DMARC advice then stops at p=quarantine.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show informational findings in addition to errors and warnings; DNS presence is not a signature check.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    domain = args.domain.lower().strip().rstrip(".")

    report = DomainReport(domain=domain, dns_backend=_DNS_BACKEND)

    check_spf(domain, report)
    check_dkim(domain, args.dkim_selectors, report)
    check_dmarc(domain, report, args.all_sources_aligned, args.mailing_list_users)
    check_bimi(domain, report)

    return print_report(report, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
