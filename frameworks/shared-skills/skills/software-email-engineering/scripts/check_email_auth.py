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
"""

from __future__ import annotations

import argparse
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
                for part in rdata.strings:
                    results.append(part.decode("utf-8", errors="replace"))
            return results
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
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
            "warning", "DKIM",
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
                "warning", "DKIM",
                f"No DKIM record found at {dkim_name}. "
                "If this selector is active, add the TXT record provided by your ESP.",
            )
            continue

        found_any = True
        dkim = dkim_records[0]
        report.add("info", "DKIM", f"DKIM record found at {dkim_name}.", record=dkim[:120] + ("..." if len(dkim) > 120 else ""))

        # Check for empty/revoked key (p=)
        p_match = re.search(r"\bp=([^;]+)", dkim)
        if p_match:
            p_value = p_match.group(1).strip()
            if not p_value:
                report.add(
                    "error", "DKIM",
                    f"DKIM key at {dkim_name} has an empty p= value — this revokes the key. "
                    "Update the record with a valid public key.",
                    record=dkim[:120],
                )
            else:
                # Rudimentary key length check for RSA (base64 length ~ key bits / 6)
                key_bits = len(p_value.replace(" ", "")) * 6 // 8 * 8
                if key_bits < 1024:
                    report.add(
                        "error", "DKIM",
                        f"DKIM key at {dkim_name} appears to be shorter than 1024 bits "
                        f"(estimated ~{key_bits} bits from key material length). "
                        "Rotate to a 2048-bit key — short keys are rejected by some providers.",
                        record=dkim[:80],
                    )
                elif key_bits < 2048:
                    report.add(
                        "warning", "DKIM",
                        f"DKIM key at {dkim_name} appears to be approximately {key_bits} bits. "
                        "2048-bit keys are recommended; 1024-bit keys are deprecated by some providers.",
                    )

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

def check_dmarc(domain: str, report: DomainReport) -> None:
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
    report.add("info", "DMARC", f"DMARC record found.", record=dmarc)

    # Policy check
    p_match = re.search(r"\bp=([^;]+)", dmarc)
    if not p_match:
        report.add("error", "DMARC", "DMARC record is missing the required p= policy tag.", record=dmarc)
    else:
        p = p_match.group(1).strip().lower()
        if p == "none":
            report.add(
                "warning", "DMARC",
                "DMARC policy is p=none — this is monitoring-only and provides zero spoofing protection. "
                "Migrate to p=quarantine then p=reject once all sending sources are authenticated. "
                "Anti-pattern: DMARC p=none indefinitely means your domain can be freely impersonated.",
                record=dmarc,
            )
        elif p == "quarantine":
            report.add(
                "info", "DMARC",
                "DMARC policy is p=quarantine. Good progress. "
                "Once you have confirmed all legitimate senders pass authentication, move to p=reject.",
            )
        elif p == "reject":
            report.add("info", "DMARC", "DMARC policy is p=reject. Full enforcement.")
        else:
            report.add("error", "DMARC", f"DMARC p= value '{p}' is not valid. Must be none, quarantine, or reject.", record=dmarc)

    # rua (aggregate reports)
    if "rua=" not in dmarc:
        report.add(
            "warning", "DMARC",
            "DMARC record is missing rua= aggregate report destination. "
            "Without aggregate reports, you cannot identify misauthenticated sending sources. "
            "Add rua=mailto:dmarc-reports@yourdomain.com or a DMARC reporting service address.",
        )

    # sp= subdomain policy
    sp_match = re.search(r"\bsp=([^;]+)", dmarc)
    if not sp_match:
        report.add(
            "warning", "DMARC",
            "DMARC record does not specify sp= subdomain policy. "
            "Subdomains inherit the root p= policy by default, but adding sp=reject explicitly "
            "protects subdomains that do not send email from being used for phishing.",
        )
    else:
        sp = sp_match.group(1).strip().lower()
        if sp == "none":
            report.add(
                "warning", "DMARC",
                "DMARC sp=none means subdomains have no spoofing protection even if the root domain has p=reject. "
                "Consider sp=reject to protect subdomains.",
            )


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
            "Requires DMARC p=quarantine or p=reject and a Verified Mark Certificate (VMC).",
        )
        return

    bimi = bimi_records[0]
    report.add("info", "BIMI", "BIMI record found.", record=bimi)

    # Check for VMC (a= tag)
    if "a=" not in bimi:
        report.add(
            "warning", "BIMI",
            "BIMI record is missing the a= (VMC authority) tag. "
            "Gmail requires a Verified Mark Certificate (VMC) to display the logo. "
            "Without a=, the BIMI logo will only display in Yahoo Mail and other clients that do not require VMC.",
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
        print("### Info (verified)")
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
  DKIM    Record presence for each provided selector, empty/revoked key, key length
  DMARC   Presence, p= policy level, rua= reports, sp= subdomain policy
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
        "--verbose", "-v",
        action="store_true",
        help="Show informational (passing) findings in addition to errors and warnings.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    domain = args.domain.lower().strip().rstrip(".")

    report = DomainReport(domain=domain, dns_backend=_DNS_BACKEND)

    check_spf(domain, report)
    check_dkim(domain, args.dkim_selectors, report)
    check_dmarc(domain, report)
    check_bimi(domain, report)

    return print_report(report, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
