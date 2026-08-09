# Email Deliverability: Sender Requirements and Authentication Reference

## Table of Contents

1. [Yahoo and Google Bulk-Sender Requirements](#1-yahoo-and-google-bulk-sender-requirements)
2. [DMARC Progression Strategy](#2-dmarc-progression-strategy)
3. [BIMI and VMC Certificates](#3-bimi-and-vmc-certificates)
4. [Microsoft 365 Sender Requirements (May 2025)](#4-microsoft-365-sender-requirements-may-2025)
5. [Apple Mail Privacy Protection Effects on Opens](#5-apple-mail-privacy-protection-effects-on-opens)
6. [Postmaster Tools and Deliverability Diagnostics](#6-postmaster-tools-and-deliverability-diagnostics)
7. [Anti-Pattern Summary](#7-anti-pattern-summary)
8. [Citations](#8-citations)

---

## 1. Yahoo and Google Bulk-Sender Requirements

### 1.1 Timeline

Google announced bulk-sender requirements in October 2023; enforcement began **February 2024** for senders of 5,000+ messages per day to Gmail. Yahoo aligned requirements went live at the same time. Enforcement tightened through 2024–2025, and in **November 2025** Gmail moved from warnings/spam-foldering to outright SMTP-level rejection (5xx permanent bounces) for bulk mail that fails authentication or exceeds spam-rate thresholds. Verify current enforcement posture — this has moved fast and may tighten further.

**Definition of bulk sender (Google):** Any domain that sends 5,000 or more messages per day to Gmail addresses. The threshold is evaluated per sending domain, not per account.

### 1.2 Three Mandatory Requirements

All bulk senders to Gmail and Yahoo must meet all three:

**1. Email authentication: SPF + DKIM + DMARC**

- SPF: A DNS TXT record (`v=spf1 include:... ~all` or `-all`) listing authorized sending IPs. Must pass alignment — the `MAIL FROM` domain must be covered.
- DKIM: A 2048-bit RSA (or Ed25519) signature on the message. The signing domain must be aligned with the `From:` header domain. Keys shorter than 1024 bits are rejected; 2048-bit is the current recommended minimum.
- DMARC: A `p=` policy of at least `none` satisfies both Google's and Microsoft's published bulk-sender minimum — Google's own guidance states "your DMARC enforcement policy can be set to none." `p=quarantine`/`p=reject` are not contractually required for bulk-sender compliance, but they are the correct target posture: `p=none` provides zero anti-spoofing protection, and both providers have signaled that stricter requirements may follow. Do not tell a customer they are non-compliant at `p=none` — they are compliant but under-protected. Verify current requirements before advising, as this is a fast-moving area.
- **Alignment rule:** DMARC alignment requires that either the SPF-authenticated domain or the DKIM signing domain matches the `From:` header domain (strict or relaxed alignment). A passing SPF or DKIM on a different subdomain does not satisfy DMARC alignment.

**2. One-click unsubscribe per RFC 8058**

- Messages with a marketing or bulk classification must include a `List-Unsubscribe` header with both a `mailto:` fallback and an `https:` URL for one-click processing.
- The HTTPS URL must process the unsubscribe within 2 business days when a POST is received. The POST body will be empty or contain `List-Unsubscribe=One-Click`.
- Gmail surfaces a one-click unsubscribe button in the UI when this header is present. Its absence for bulk senders is treated as a deliverability signal.
- RFC 8058 requires: `List-Unsubscribe-Post: List-Unsubscribe=One-Click` header alongside the `List-Unsubscribe` header to explicitly opt in to one-click processing.

```
List-Unsubscribe: <https://example.com/unsubscribe?token=abc123>, <mailto:unsub@example.com?subject=unsubscribe>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

**3. Spam rate below 0.3%**

- Google Postmaster Tools reports spam rate as a percentage of messages flagged by Gmail users.
- Google's published guidance: keep spam rate below 0.10% consistently (this is the working target, not just a suggestion); 0.30% or higher is the hard threshold that breaks bulk-sender compliance and blocks eligibility for delivery mitigation. Google restores mitigation eligibility only after spam rate stays below 0.30% for 7 consecutive days.
- Yahoo uses similar internal thresholds.
- Spam rate is a lagging indicator: by the time it exceeds 0.3%, deliverability damage is already accumulating. Monitor continuously with Postmaster Tools, not reactively.

### 1.3 Additional Requirements

- **TLS in transit:** All messages must be sent over TLS. Most ESPs handle this automatically.
- **PTR / Reverse DNS:** Sending IPs must have valid PTR records that resolve forward. Shared ESP IPs typically have this configured. Self-managed sending IPs require manual PTR setup.
- **RFC 5322 compliance:** Valid `Message-ID` header, valid `Date` header, valid `From:` with a real domain.
- **No misleading `From:` headers:** The `From:` display name and address must accurately represent the sending organization.

---

## 2. DMARC Progression Strategy

### 2.1 Why `p=none` Is Not an End State

`p=none` instructs receiving servers to take no action on authentication failures — it only enables reporting. Senders stuck at `p=none` provide zero protection against domain spoofing and phishing using their domain.

The progression to `p=reject` is the standard practice:

```
p=none   → Monitor reports, identify legitimate sending sources
p=quarantine → Failed messages go to spam; catch misconfigured senders
p=reject → Failed messages are rejected outright; full spoofing protection
```

### 2.2 Safe Progression Steps

**Step 1: Deploy `p=none` with reporting.**

```dns
_dmarc.yourdomain.com TXT "v=DMARC1; p=none; rua=mailto:dmarc-reports@yourdomain.com; ruf=mailto:dmarc-failures@yourdomain.com; pct=100"
```

- `rua`: Aggregate reports (daily, sent by receiving servers). Use a DMARC reporting service (Postmark, Dmarcian, Valimail) to parse and visualize.
- `ruf`: Forensic/failure reports (per-message, PII implications — treat carefully). Some providers no longer send `ruf` reports due to privacy concerns.
- Review aggregate reports for 2-4 weeks before moving to `quarantine`.

**Step 2: Identify all legitimate sending sources.**

Aggregate reports list every IP that sent mail claiming your domain. Common sources missed during initial review:
- Marketing ESPs (Mailchimp, HubSpot)
- CRM transactional triggers
- Customer support tools (Zendesk, Intercom)
- Calendar invites from Google Workspace / Microsoft 365
- Legacy cron jobs and application mailers
- Third-party SaaS integrations that send on your behalf

For each source, either: (a) add it to SPF and configure DKIM, or (b) stop it from using your domain.

**Step 3: Move to `p=quarantine` with `pct=10`.**

Start with a small percentage to catch any sources you missed:

```dns
v=DMARC1; p=quarantine; pct=10; rua=mailto:dmarc-reports@yourdomain.com
```

Monitor bounce rates and complaints. Increase `pct` by 10-25 percentage points each week if clean.

**Step 4: Move to `p=reject`.**

```dns
v=DMARC1; p=reject; pct=100; rua=mailto:dmarc-reports@yourdomain.com
```

This is the target state. It stops all domain spoofing and satisfies Google/Yahoo sender requirements fully.

### 2.3 Subdomain Policy

The `sp=` tag controls the DMARC policy for subdomains. Use `sp=reject` to extend the root domain's protection to all subdomains, including those that do not send email (a common phishing vector):

```dns
v=DMARC1; p=reject; sp=reject; rua=mailto:dmarc-reports@yourdomain.com
```

### 2.4 Why This Still Matters at Scale (Expert Judgment)

DMARC record publication has grown steadily (roughly half of internet domains now publish some DMARC record, per 2026 adoption studies), but enforcement lags badly — only a low-single-digit percentage of all domains enforce `p=reject`, and even among domains actively engaged with DMARC, only a minority reach full enforcement. Large enterprises reach `p=reject` at several times the rate of small/mid-size companies. Practical implication: never assume a counterparty domain is spoofing-protected because "they probably have DMARC" — verify the actual policy tag, and treat your own progression to `p=reject` as a genuine security control, not paperwork, since most peer domains still haven't done it. Verify current adoption figures before quoting a specific percentage; they move year over year.

---

## 3. BIMI and VMC Certificates

### 3.1 BIMI Overview

Brand Indicators for Message Identification (BIMI) enables verified sender logos to appear in supporting email clients (Gmail, Yahoo Mail, Apple Mail, Fastmail). It requires:

1. A published BIMI DNS record pointing to an SVG logo.
2. A certificate proving logo ownership from a BIMI-accredited Mark Verifying Authority (MVA) — see 3.1.1 below for which certificate type and which CAs currently qualify.
3. DMARC at `p=quarantine` or `p=reject` (not `p=none`) — this is a real, hard BIMI-specific requirement, distinct from the `p=none` bulk-sender compliance floor in Section 1.

**Gmail requirement:** As of 2025–2026 Gmail accepts either a VMC or a Common Mark Certificate (CMC — see below) to display the logo, but only a VMC unlocks the blue verified-checkmark treatment. Apple Mail requires a VMC specifically; CMC is not accepted there. Yahoo Mail displays BIMI logos more permissively. Verify current per-provider acceptance before final advice — this has changed materially since 2024 and each mailbox provider sets its own MVA trust list independently of the BIMI spec.

### 3.1.1 VMC vs. CMC and the current CA landscape

- **VMC (Verified Mark Certificate):** Requires a registered trademark. Issued by a BIMI-accredited CA after trademark validation (2–4 weeks typical). Unlocks the Gmail blue checkmark and is required for Apple Mail.
- **CMC (Common Mark Certificate):** Introduced by the BIMI working group as a lower-friction alternative for brands without a registered trademark — the CA instead verifies 12+ months of public logo use on a domain you control (via web-archive evidence). Accepted by Gmail (no checkmark), not accepted by Apple Mail.
- **CA landscape has shifted:** Entrust exited the public BIMI-certificate business (its public CA business was sold to Sectigo), and Google and Apple stopped trusting Entrust-issued certificates as of November 2024. Do not recommend Entrust for new VMC/CMC purchases. As of 2026, DigiCert remains a primary issuer, with GlobalSign, SSL.com, and Sectigo also active in the market. The AuthIndicators Working Group does not itself certify MVAs — each mailbox provider independently decides which CAs it trusts, so verify current acceptance with the specific target mailbox providers (especially Gmail and Apple Mail) before purchasing a certificate, not just against the BIMI Group's issuer list.

### 3.2 BIMI DNS Record

```dns
default._bimi.yourdomain.com TXT "v=BIMI1; l=https://yourdomain.com/bimi-logo.svg; a=https://yourdomain.com/bimi.pem"
```

- `l=`: URL to the BIMI SVG file. Must be HTTPS, must be SVG Tiny P/S format, must be < 32KB.
- `a=`: URL to the VMC certificate in PEM format.

### 3.3 VMC Process and Cost

1. Apply for a trademark in your jurisdiction (or provide evidence of existing trademark), or use the CMC path (Section 3.1.1) if no trademark exists.
2. Purchase a VMC from a currently BIMI-accredited CA — DigiCert is the long-standing primary issuer; GlobalSign and SSL.com have also entered the market. Do not use Entrust for new purchases (see 3.1.1). Verify current authorized CAs and pricing before committing, since this list has changed materially since 2024.
3. The CA validates the trademark (VMC) or logo-usage history (CMC) and issues the certificate.
4. Host the PEM file at the URL in the BIMI record.

VMC issuance typically takes 2-4 weeks depending on trademark validation requirements (CMC issuance is comparable or faster, since it checks usage history rather than a trademark registry). Plan ahead before a major brand campaign. Verify current issuance timelines and pricing — both move with CA competition.

---

## 4. Microsoft 365 Sender Requirements (May 2025)

Microsoft announced these bulk-sender requirements in April 2025 and began enforcement May 5, 2025, for Exchange Online and Outlook.com. Microsoft's original plan was to route non-compliant bulk mail to the Junk folder; before rollout completed, Microsoft changed this to outright SMTP rejection instead. Verify current enforcement status — this is understood to remain fully active through 2026.

### 4.1 Key Changes

- **DMARC enforcement for high-volume senders:** Domains sending more than 5,000 messages per day to Outlook.com / Hotmail / Live.com must have DMARC at a minimum of `p=none`, aligned with SPF or DKIM (preferably both) — the same floor Google applies, not the stricter `p=quarantine`/`p=reject` bar. Non-compliant mail is rejected with SMTP code `550 5.7.515 Access denied, sending domain ... does not meet the required authentication level`. `p=quarantine`/`p=reject` are not contractually required but remain the correct target posture for the same reasons given in Section 2.
- **Composite authentication scoring:** Microsoft evaluates SPF, DKIM, DMARC, and additional signals (sender reputation, list hygiene, engagement rates) as a composite score. A passing SPF alone is insufficient — full alignment is required.
- **Postmaster portal:** Microsoft offers a Junk Mail Reporting Program and a Sender Support portal (postmaster.live.com) for investigating delivery issues to Microsoft-hosted mailboxes.
- **ARC (Authenticated Received Chain):** Microsoft supports ARC sealing for forwarded mail. If your mail passes through a mailing list or forwarding service that breaks DKIM, ARC allows the final hop to attest to the original authentication state.

### 4.2 Recommendations for Microsoft-Heavy Recipient Bases

- `p=none` aligned to SPF or DKIM meets Microsoft's published compliance floor, but reach `p=reject` before targeting Microsoft-hosted mailboxes at volume — the floor buys compliance, not protection or long-term headroom.
- Monitor the Microsoft SNDS (Smart Network Data Services) for IP reputation and complaint data.
- If you use a third-party ESP, verify they have a partnership with Microsoft or maintain good IP reputation in the SNDS.
- Enable ARC signing at your ESP or gateway if your mail passes through forwarding hops.

---

## 5. Apple Mail Privacy Protection Effects on Opens

### 5.1 What MPP Does

Apple Mail Privacy Protection (MPP), introduced in iOS 15 and macOS Monterey (2021), prefetches email content including tracking pixels using Apple's proxy servers. The effect:

- Open pixels fire when Apple's proxy fetches the email, not when the user reads it.
- This happens regardless of whether the user actually opens the email.
- Apple randomizes the fetch timing, so the "open time" in your ESP is unreliable.

### 5.2 Impact on Metrics

**Inflated open rates:** As of 2026, Litmus Email Analytics reports MPP affecting roughly 55–60% of tracked opens, and Apple Mail (iPhone + iPad + macOS, combined with MPP-affected opens) holds the largest single-client share of the email market — commonly cited around 45–52% depending on methodology and dataset. Figures move with each Litmus/analytics refresh; verify current numbers before quoting a specific percentage, but the directional fact — a majority of opens are Apple-proxy-inflated and unreliable — has been stable for several years and is not expected to reverse.

**Broken time-of-open signals:** Send-time optimization features that rely on "when did this user open?" signals are unreliable for Apple Mail users.

**Broken re-engagement logic:** If your automation marks a subscriber as "re-engaged" on any open, MPP will falsely re-engage Apple Mail users.

**iOS 26 compounds the measurement problem, it doesn't just add noise to it.** Apple Mail's inbox categorization (Primary / Transactions / Updates / Promotions) and on-device AI summaries now change which emails a human ever sees prominently, not just whether the open pixel fires honestly. A marketing email sorted into "Promotions" and reduced to an AI-generated one-line summary competes for attention very differently than in a flat, chronological inbox — expect click-through rates themselves to soften for senders who don't earn Primary/Updates placement, independent of any MPP effect on opens.

### 5.3 Adaptation Strategies — expert judgment on what still matters

- **Stop using opens as a primary engagement signal.** Move to click-through rate, conversion rate, and reply rate as the primary indicators of list health. This is no longer a hedge — it is the baseline, non-negotiable measurement posture for any list with meaningful Apple Mail share.
- **Segment by client.** Use the `X-Mailer` or user-agent header (where available) to identify Apple Mail users. Apply different re-engagement logic for this segment.
- **Use click data for list hygiene.** Suppress subscribers who have not clicked in 6-12 months, not those who have not "opened."
- **Report on adjusted open rate.** Some ESPs offer an "adjusted open rate" that subtracts Apple MPP-triggered opens. Use this for trend analysis, not as a headline metric.
- **Do not infer consent or re-engagement from MPP opens.** If your application requires explicit consent or engagement confirmation, opens are no longer sufficient for this purpose.
- **Design for the Primary/Updates tab, not just the message body.** Subject line clarity, sender reputation, and per-recipient engagement history now influence whether Apple's on-device categorization treats a sender as Primary-worthy or Promotions-worthy — this is a new lever, not just a rendering concern.

---

## 6. Postmaster Tools and Deliverability Diagnostics

### 6.1 Google Postmaster Tools

URL: https://postmaster.google.com

Requires domain verification (DNS TXT record). Google has been rolling out **Postmaster Tools V2** since early-to-mid 2026, which reframes the tool from a reputation dashboard to a compliance dashboard. Provides:

- **Domain reputation:** High / Medium / Low / Bad — based on Google's internal signals across all Gmail users. Still present in V2 but no longer the headline signal.
- **IP reputation:** Same scale, per sending IP.
- **Spam rate:** Percentage of mail flagged as spam by Gmail users, now shown to two decimal places in V2 with the 0.10%/0.30% thresholds surfaced explicitly. Updated daily.
- **Compliance status / Deliverability analysis (V2):** A dedicated section that translates spam rate, authentication errors, SMTP errors, volume, and user feedback into a plain-language compliant/non-compliant verdict plus a recommended action — a binary compliance check rather than a vague reputation score.
- **Authentication:** SPF, DKIM, DMARC pass rates as percentages.
- **Delivery errors:** Types and counts of SMTP rejection codes.
- **Encryption:** TLS usage rates.
- **User-reported spam:** Complaint feedback loop data.

**Reading domain reputation:** "High" is the target. "Medium" signals emerging problems. "Low" means significant deliverability impact. "Bad" means most mail is being spam-folded or rejected. In V2, treat the compliance-status verdict as the primary read and the reputation scale as secondary context — verify current V2 rollout status and terminology before final advice, since Google is actively iterating on this interface.

### 6.2 Yahoo Postmaster Tools

URL: https://senders.yahooinc.com

Provides:

- Complaint rate feedback loop (requires application to Yahoo's FBL program).
- Sender reputation score and delivery statistics for Yahoo Mail / AOL Mail.
- IP and domain reputation lookups.

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
- Blacklist check across 100+ DNSBLs
- Email header analyzer (trace the authentication chain in a real message header)
- SMTP diagnostics (test SMTP connectivity and banner)

Use MXToolbox's "Email Header Analyzer" when debugging a specific message that failed authentication — it traces every hop and shows where SPF/DKIM/DMARC checks were performed.

### 6.5 GlassWall / Inbox Placement Testing

Services like GlassWall, Litmus Email Analytics, and 250ok (now part of Validity) offer inbox placement testing: send a test message to seed accounts across major ISPs and report whether each delivery reached the inbox, spam folder, or was rejected. Note that Validity acquired Litmus (announced April 2025, deal completed ~March 2026); Litmus pricing rose sharply post-acquisition and product roadmap questions (whether Litmus stays standalone vs. folds into Validity's Everest platform) were still unsettled as of mid-2026 — verify current Litmus pricing/positioning before recommending it as the default choice, and consider Email on Acid (still independent) as a comparison point.

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
| Using opens as list-health signal | Apple MPP inflates roughly 55-60% of tracked opens as of 2026 (Litmus Email Analytics — verify current figure). Open-based re-engagement or suppression logic will behave incorrectly. Use clicks and conversions. |
| Shared sending domain for transactional and marketing | Marketing complaint rates damage the shared domain's reputation, causing transactional mail (password resets, receipts) to land in spam during campaign periods. Always use separate subdomains. |
| DKIM keys shorter than 2048 bits | 1024-bit DKIM keys are considered weak and some providers reject them. Generate 2048-bit keys; rotate annually or on any key compromise suspicion. |
| Not monitoring Postmaster Tools | Reputation problems surface days or weeks before delivery collapse. Postmaster Tools is the only way to see Google's view of your sending reputation in time to act. |
| Ignoring DMARC aggregate reports during `p=none` phase | Aggregate reports identify every sending source using your domain. Skipping this analysis means moving to `p=quarantine` with unknown legitimate senders, causing broken deliverability for services you forgot about. |

---

## 8. Citations

- **Google Email Sender Guidelines:** https://support.google.com/a/answer/81126 — Bulk sender requirements, DMARC `p=none` minimum, spam rate thresholds, one-click unsubscribe enforcement. Also see the FAQ: https://support.google.com/a/answer/14229414 — spam-rate mitigation-eligibility rules (0.10%/0.30%, 7-consecutive-day recovery window).
- **Yahoo Sender Requirements:** https://senders.yahooinc.com/best-practices — Aligned requirements with Google, enforcement timeline.
- **RFC 8058 — One-Click Unsubscribe:** https://www.rfc-editor.org/rfc/rfc8058 — Specification for `List-Unsubscribe-Post: List-Unsubscribe=One-Click`.
- **RFC 9989, 9990, 9991 — DMARCbis (published May 2026):** https://www.rfc-editor.org/rfc/rfc9989 — Obsoletes RFC 7489 (and RFC 9091's `psd=` tag), splits the spec into core protocol / aggregate reporting / failure reporting, and promotes DMARC to IETF Standards Track for the first time. `v=DMARC1` records and the `p`, `sp`, `rua`, `ruf`, `adkim`, `aspf`, `fo` tags are unchanged; `pct`, `rf`, and `ri` are deprecated. Verify current status if citing tag-level behavior.
- **RFC 6376 — DKIM:** https://www.rfc-editor.org/rfc/rfc6376 — DKIM specification.
- **RFC 7208 — SPF:** https://www.rfc-editor.org/rfc/rfc7208 — SPF specification.
- **BIMI Working Group:** https://bimigroup.org — BIMI specification, VMC/CMC requirements, MVA issuer list, adoption status.
- **Microsoft Sender Requirements (May 2025):** https://sendersupport.olc.protection.outlook.com/pm/policies.aspx — also see Microsoft Tech Community announcement for the SMTP `550 5.7.515` rejection behavior.
- **Google Postmaster Tools:** https://postmaster.google.com — now rolling out as Postmaster Tools V2 with a compliance-status/deliverability-analysis view; verify current UI terminology.
- **Mail-Tester:** https://www.mail-tester.com
- **MXToolbox:** https://mxtoolbox.com
- **Litmus Email Client Market Share:** https://www.litmus.com/email-client-market-share — Apple Mail/MPP share and open-rate inflation figures; note Litmus is now part of Validity (acquisition completed ~March 2026), verify current pricing before recommending.
