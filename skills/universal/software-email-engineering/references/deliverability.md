# Email Deliverability: Sender Requirements and Authentication Reference

## Table of Contents

1. [Yahoo and Google Bulk-Sender Requirements](#1-yahoo-and-google-bulk-sender-requirements)
2. [DMARC Progression Strategy](#2-dmarc-progression-strategy)
3. [BIMI and VMC Certificates](#3-bimi-and-vmc-certificates)
4. [Outlook.com Consumer High-Volume Sender Requirements (May 2025)](#4-outlookcom-consumer-high-volume-sender-requirements-may-2025)
5. [Apple Mail Privacy Protection (pointer)](#5-apple-mail-privacy-protection-pointer)
6. [Postmaster Tools and Deliverability Diagnostics](#6-postmaster-tools-and-deliverability-diagnostics)
7. [Anti-Pattern Summary](#7-anti-pattern-summary)
8. [Citations](#8-citations)
9. [Transport Security: MTA-STS and TLS-RPT](#9-transport-security-mta-sts-and-tls-rpt)

---

## 1. Yahoo and Google Bulk-Sender Requirements

Google/Yahoo bulk-sender scope, complaint thresholds, unsubscribe timing, and enforcement are owned by marketing-email-automation. Use its official provider links before configuring a sending policy; Yahoo does not publish Google's numeric bulk-volume boundary. This reference owns authentication mechanics.

**DKIM algorithm choice:** Prefer RSA-SHA256 with at least 2048-bit RSA for interoperability. [RFC 8301 §3.2](https://www.rfc-editor.org/rfc/rfc8301#section-3.2) permits 1024-bit RSA and recommends 2048-bit; keys below 1024-bit are invalid. [RFC 8463 §6](https://www.rfc-editor.org/rfc/rfc8463#section-6) permits adding Ed25519-SHA256 alongside RSA-SHA256 with separate selectors. Do not replace RSA with Ed25519 until your ESP and recipient receivers have verified support.

**DMARC alignment:** A passing SPF envelope-sender identity or DKIM `d=` identity must align with the visible `From:` domain. Relaxed alignment permits identities sharing an organizational domain; strict alignment requires an exact domain match. SPF and DKIM passing on unrelated domains do not pass DMARC.

**RFC 8058 handler:** Supply an HTTPS URI in `List-Unsubscribe` and `List-Unsubscribe-Post: List-Unsubscribe=One-Click`; a `mailto:` fallback is optional. DKIM must cover both headers. Accept the one-click form POST without login or a confirmation step, and durably apply the relevant list suppression. A GET must not unsubscribe, because scanners may follow links. Purely transactional mail requires separate classification from marketing/subscribed mail.

```text
List-Unsubscribe: <https://example.com/unsubscribe?token=opaque>, <mailto:unsub@example.com>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

---

## 2. DMARC Progression Strategy

### 2.1 Why `p=none` Is Not an End State

`p=none` instructs receiving servers to take no action on authentication failures — it only enables reporting. Senders stuck at `p=none` provide zero protection against domain spoofing and phishing using their domain.

DMARCbis (RFC 9989, Standards Track) obsoletes RFC 7489 and RFC 9091 and changes the progression:

- `pct`, `rf`, and `ri` are **removed**. Operational experience showed `pct` was rarely applied accurately except at 0 or 100, so do not build a percentage ramp.
- `t=y` (test mode) replaces the useful part of `pct`: the receiver applies the published policy **one level down** (`p=quarantine; t=y` → treated as `none`; `p=reject; t=y` → treated as `quarantine`) plus any special handling such as `From:` rewriting. Reports are unaffected.
- `np=` (imported from RFC 9091) sets the policy for **non-existent** subdomains; `sp=` covers existing subdomains.
- `psd=` is new: public-suffix operators flag a PSD; ordinary senders leave it at the default.
- Organizational-domain discovery uses a DNS tree walk instead of the Public Suffix List.
- Domains that host users who might post to mailing lists **SHOULD NOT** publish `p=reject`. If such a domain still wants reject, RFC 9989 says to run `p=none` for at least a month, then `p=quarantine` for an equally long period, compare dispositions, and tell users list participation may be hindered.

```
p=none        → Monitor reports, identify legitimate sending sources
p=quarantine  → Failed messages go to spam; catch misconfigured senders (optionally t=y first)
p=reject      → Failed messages are rejected; for transactional-only or non-mailbox domains
```

### 2.2 Safe Progression Steps

**Step 1: Deploy `p=none` with reporting.**

```dns
_dmarc.yourdomain.com TXT "v=DMARC1; p=none; rua=mailto:dmarc-reports@yourdomain.com; ruf=mailto:dmarc-failures@yourdomain.com"
```

- `rua`: Aggregate reports (daily, sent by receiving servers). Use a DMARC reporting service (Postmark, Dmarcian, Valimail) to parse and visualize.
- `ruf`: Forensic/failure reports (per-message, PII implications — treat carefully). Some providers no longer send `ruf` reports due to privacy concerns.
- Review aggregate reports for at least a month before moving to `quarantine`.

**Step 2: Identify all legitimate sending sources.**

Aggregate reports list every IP that sent mail claiming your domain. Common sources missed during initial review:
- Marketing ESPs (Mailchimp, HubSpot)
- CRM transactional triggers
- Customer support tools (Zendesk, Intercom)
- Calendar invites from Google Workspace / Microsoft 365
- Legacy cron jobs and application mailers
- Third-party SaaS integrations that send on your behalf

For each source, either: (a) add it to SPF and configure DKIM, or (b) stop it from using your domain. A domain that will publish `p=reject` must DKIM-sign its mail rather than rely on SPF alone (RFC 9989).

**Step 3: Move to `p=quarantine`, optionally in test mode first.**

```dns
v=DMARC1; p=quarantine; t=y; rua=mailto:dmarc-reports@yourdomain.com
```

With `t=y` receivers treat failures as `none` while you watch reports; then drop `t=y`:

```dns
v=DMARC1; p=quarantine; np=reject; rua=mailto:dmarc-reports@yourdomain.com
```

Monitor bounce rates, complaints, and aggregate reports for a period at least as long as the `p=none` phase.

**Step 4: Choose the end state per domain.**

```dns
v=DMARC1; p=reject; np=reject; rua=mailto:dmarc-reports@yourdomain.com
```

- **Transactional-only or non-mailbox subdomains** (e.g., `mail.example.com`, parked domains): `p=reject` is the target.
- **Domains whose human users post to mailing lists** (typically the organizational domain with Workspace/M365 mailboxes): RFC 9989 says SHOULD NOT publish `p=reject`; stay at `p=quarantine`, or accept the mailing-list breakage explicitly and tell users.

### 2.3 Subdomain Policy

The `sp=` tag controls the DMARC policy for existing subdomains; `np=` controls non-existent subdomains (a common phishing vector). If `np` is absent, `sp` (or else `p`) applies:

```dns
v=DMARC1; p=quarantine; sp=reject; np=reject; rua=mailto:dmarc-reports@yourdomain.com
```

### 2.4 Why This Still Matters at Scale (Expert Judgment)

Publishing a DMARC record is far more common than enforcing one: many domains stop at `p=none`. Practical implication: never assume a counterparty domain is spoofing-protected because "they probably have DMARC" — verify the actual policy tag, and treat your own progression to `p=reject` as a genuine security control, not paperwork, since many peer domains have not done it. Quote adoption percentages only from a current, cited study.

---

## 3. BIMI and VMC Certificates

### 3.1 BIMI Overview

Brand Indicators for Message Identification (BIMI) enables verified sender logos to appear in supporting email clients (Gmail, Yahoo Mail, Apple Mail, Fastmail). It requires:

1. A published BIMI DNS record pointing to an SVG logo.
2. A certificate proving logo ownership from a BIMI-accredited Mark Verifying Authority (MVA) — see 3.1.1 below for which certificate type and which CAs currently qualify.
3. DMARC at `p=quarantine` or `p=reject` (not `p=none`) — this is a real, hard BIMI-specific requirement, distinct from the `p=none` bulk-sender compliance floor in Section 1.

**Per-provider acceptance (VMC vs CMC, checkmark, Yahoo/Apple/Outlook behaviour) and the brand decision** are owned by marketing-email-automation/references/deliverability.md. This section keeps the DNS and certificate mechanics. Note that the BIMI DMARC prerequisite interacts with the RFC 9989 mailing-list caveat: a mailbox domain that stays at `p=quarantine` still qualifies.

### 3.1.1 Certificate Choice

Use the marketing-owned BIMI decision for VMC/CMC selection. Before buying, check each target mailbox provider's accepted certificate type and issuer, then obtain an issuance-time and price quote from that issuer; the BIMI Group's issuer list alone does not establish mailbox-provider trust.

### 3.2 BIMI DNS Record

```dns
default._bimi.yourdomain.com TXT "v=BIMI1; l=https://yourdomain.com/bimi-logo.svg; a=https://yourdomain.com/bimi.pem"
```

- `l=`: URL to the BIMI SVG file. Use HTTPS and SVG Tiny P/S; verify the target mailbox provider's current size and format limits before publishing.
- `a=`: URL to the accepted mark certificate in PEM format.

### 3.3 Certificate Deployment

Confirm trademark or logo-history evidence with the selected issuer, complete its validation, and host the issued PEM at the BIMI record's `a=` URL. Check the SVG and certificate URLs from outside the origin network. Verify display with the target providers; a valid DNS record alone does not guarantee a logo or checkmark.

---

## 4. Outlook.com Consumer High-Volume Sender Requirements (May 2025)

Microsoft announced these requirements in April 2025 and began enforcement May 5, 2025. They apply to **Microsoft's consumer services only** — Outlook.com, Hotmail, Live.com, MSN — not to Microsoft 365 / Exchange Online tenants. Microsoft's original plan was to route non-compliant mail to Junk; it changed this to outright rejection. Verify current enforcement status before advising.

### 4.1 Requirements (domains sending more than 5,000 messages/day to Microsoft consumer addresses)

- **SPF must pass** and **DKIM must pass** — both, not either. A sender whose SPF fails but whose aligned DKIM passes DMARC is still rejected by Outlook.com.
- **DMARC** at a minimum of `p=none`, aligned with at least one of SPF or DKIM (Microsoft: "preferably both"). `p=quarantine`/`p=reject` are not required but remain the target posture (Section 2).
- Non-compliant mail is rejected with `550 5.7.515 Access denied, sending domain ... does not meet the required authentication level`.
- **Recommendations, not requirements:** a functional unsubscribe link, list hygiene, and complaint management appear under Microsoft's "additional email hygiene recommendations".
- **ARC:** Microsoft supports ARC for forwarded mail. If your mail passes through a mailing list or forwarding service that breaks DKIM, ARC lets the final hop attest to the original authentication state.

### 4.2 Recommendations for Microsoft-Heavy Recipient Bases

- Confirm DKIM signing on every sending source before volume ramps — the both-must-pass rule is the most common cause of a 5.7.515 spike after adding a new sender.
- Monitor Microsoft SNDS (Smart Network Data Services) for IP reputation and complaint data, and enrol in the Junk Mail Reporting Program.
- If you use a third-party ESP, verify it maintains good IP reputation in SNDS.
- Enable ARC signing at your ESP or gateway if your mail passes through forwarding hops.

---

## 5. Apple Mail Privacy Protection (pointer)

MPP measurement effects, Apple Mail categories, and open-rate adaptation are owned by marketing-email-automation/references/deliverability.md. The engineering rule: **do not infer consent, engagement, or re-engagement from open-pixel events** — Apple's proxy prefetches pixels whether or not the user reads the message, without demonstrating a human read. Suppression, consent, and re-engagement code paths must key on clicks, replies, or explicit user actions.

---

## 6. Postmaster Tools and Deliverability Diagnostics

### 6.1 Google Postmaster Tools

URL: https://postmaster.google.com

Verify the domain through DNS, then inspect the current dashboard/help for available authentication, spam-rate, reputation, encryption, compliance, and SMTP-error views. Correlate mailbox-provider data with actual ESP bounce codes and event time; dashboard names, thresholds, and visibility change. Use the marketing-owned requirements to interpret the provider's metric rather than copying a remembered threshold.

### 6.2 Yahoo Postmaster Tools

URL: https://senders.yahooinc.com

Use its published complaint-feedback-loop enrollment and sender support guidance. Check which feedback and reputation data are actually available to this sender; do not promise a Google-style dashboard or an unpublished numeric bulk boundary.

### 6.3 Mail-Tester

URL: https://www.mail-tester.com

Send a test email to a generated address and receive a score (out of 10) that checks:

- SPF, DKIM, DMARC configuration and alignment
- Content spam score (SpamAssassin rules)
- Blacklist status across major DNS blacklists
- Message structure and header validity
- Link reputation

Use Mail-Tester for pre-deployment checks when setting up a new sending domain or template.

### 6.4 MXToolbox

URL: https://mxtoolbox.com

Diagnostic tools for:

- DNS record lookup and syntax validation (SPF, DKIM, DMARC, MX, PTR)
- Blacklist checks (verify current coverage)
- Email header analyzer (trace the authentication chain in a real message header)
- SMTP diagnostics (test SMTP connectivity and banner)

Use MXToolbox's "Email Header Analyzer" when debugging a specific message that failed authentication — it traces every hop and shows where SPF/DKIM/DMARC checks were performed.

### 6.5 GlassWall / Inbox Placement Testing

Choose a provider offering seed-inbox placement tests for the recipient mailbox mix, and verify its current coverage and price. Seed tests report those accounts' outcomes; they do not establish placement for every recipient.

Use inbox placement testing:
- Before a major campaign or new template launch
- After a domain reputation drop
- When entering a new market with different dominant email clients
- After IP warm-up to verify inbox placement before scaling volume

---

## 7. Anti-Pattern Summary

| Anti-Pattern | Reason |
|---|---|
| DMARC `p=none` indefinitely | `p=none` provides zero protection against domain spoofing and phishing. It is a monitoring-only state. Staying at `p=none` permanently means your domain can be freely impersonated for phishing attacks targeting your users. |
| One-click unsubscribe header implicit, not explicit | RFC 8058 requires the `List-Unsubscribe-Post: List-Unsubscribe=One-Click` header explicitly. Without it, Gmail does not treat the `https:` URL as one-click capable, and the sender fails Google's bulk sender requirement. |
| Using opens as consent or engagement signal | Apple MPP may proxy-fetch pixels without a human reading the message. Open-based re-engagement or suppression logic will behave incorrectly. Use clicks, replies, and explicit actions. |
| Shared sending domain for transactional and marketing | Marketing complaint rates damage the shared domain's reputation, causing transactional mail (password resets, receipts) to land in spam during campaign periods. Always use separate subdomains. |
| Confusing RSA recommendations with validity | RFC 8301 permits 1024-bit RSA and recommends 2048-bit. Generate 2048-bit RSA; verify provider policy and rotate on suspected compromise. |
| Not monitoring Postmaster Tools | Reputation problems surface days or weeks before delivery collapse. Postmaster Tools is the only way to see Google's view of your sending reputation in time to act. |
| Ignoring DMARC aggregate reports during `p=none` phase | Aggregate reports identify every sending source using your domain. Skipping this analysis means moving to `p=quarantine` with unknown legitimate senders, causing broken deliverability for services you forgot about. |

---

## 8. Citations

- **Google Email Sender Guidelines:** https://support.google.com/a/answer/81126 — Bulk sender requirements, DMARC `p=none` minimum, spam rate thresholds, one-click unsubscribe enforcement. Also see the FAQ: https://support.google.com/a/answer/14229414 — spam-rate mitigation-eligibility rules (0.10%/0.30%, 7-consecutive-day recovery window), the 48-hour unsubscribe recommendation, and the November 2025 "temporary and permanent rejections" ramp.
- **Yahoo Sender Requirements:** https://senders.yahooinc.com/best-practices — Aligned requirements with Google, enforcement timeline.
- **RFC 8058 — One-Click Unsubscribe:** https://www.rfc-editor.org/rfc/rfc8058 — Specification for `List-Unsubscribe-Post: List-Unsubscribe=One-Click`.
- **RFC 9989, 9990, 9991 — DMARCbis:** https://www.rfc-editor.org/rfc/rfc9989 — Obsoletes RFC 7489 and RFC 9091, splits the spec into core protocol (9989) / aggregate reporting (9990) / failure reporting (9991), and puts DMARC on the IETF Standards Track. `v=DMARC1` records and the `p`, `sp`, `rua`, `ruf`, `adkim`, `aspf`, `fo` tags carry over; `pct`, `rf`, and `ri` are **removed** (Appendix C.5.2); `np` (imported from RFC 9091), `psd` (new), and `t` (test mode) are added (C.5.1); the PSL is replaced by a DNS tree walk (§4.10); domains whose users post to mailing lists SHOULD NOT publish `p=reject` (§7.4).
- **RFC 6376 — DKIM:** https://www.rfc-editor.org/rfc/rfc6376 — DKIM specification.
- **RFC 7208 — SPF:** https://www.rfc-editor.org/rfc/rfc7208 — SPF specification.
- **BIMI Working Group:** https://bimigroup.org — BIMI specification, VMC/CMC requirements, MVA issuer list, adoption status.
- **Microsoft Outlook.com consumer sender requirements (May 2025):** https://support.microsoft.com/en-us/outlook/fix-ndr-error-550-5-7-515-in-outlook-com (SPF and DKIM must both pass; at least one must align; consumer services only) and the Microsoft Tech Community announcement https://techcommunity.microsoft.com/blog/microsoftdefenderforoffice365blog/strengthening-email-ecosystem-outlook%E2%80%99s-new-requirements-for-high%E2%80%90volume-senders/4399730 (`550 5.7.515` rejection; unsubscribe link listed as a recommendation).
- **Google Postmaster Tools:** https://postmaster.google.com — check the current UI for its view names and compliance-status reporting.
- **Mail-Tester:** https://www.mail-tester.com
- **MXToolbox:** https://mxtoolbox.com
- **Litmus Email Client Market Share:** https://www.litmus.com/email-client-market-share — Apple Mail/MPP share and open-rate inflation figures; Litmus is part of Validity — check current pricing before recommending.

## 9. Transport Security: MTA-STS and TLS-RPT

For a domain receiving mail, [MTA-STS (RFC 8461)](https://www.rfc-editor.org/rfc/rfc8461) publishes expected MX hosts and authenticated TLS policy. Publish `_mta-sts.example.com` TXT with `v=STSv1; id=<revision>` and serve a valid HTTPS certificate plus `https://mta-sts.example.com/.well-known/mta-sts.txt` containing `version: STSv1`, `mode: testing`, one `mx:` per permitted host, and a chosen `max_age` in seconds. Change the TXT `id` when changing policy. Verify every primary/backup MX and certificate before changing to `mode: enforce`; conforming senders defer delivery on validation failure rather than silently falling back. Account for cached policies when retiring MX hosts or removing enforcement.

Pair this with [TLS-RPT (RFC 8460)](https://www.rfc-editor.org/rfc/rfc8460): publish `_smtp._tls.example.com` TXT `v=TLSRPTv1; rua=mailto:tls-reports@example.com` and review aggregate failures for certificate, STARTTLS, and policy mismatches. TLS-RPT reports outcomes; it does not enforce transport security. MTA-STS protects delivery to your inbound domain, while outbound protection depends on the sender honoring recipient policies. With an ESP, verify its MTA-STS support and telemetry rather than treating a DNS record on your sending domain as proof of encrypted delivery.
