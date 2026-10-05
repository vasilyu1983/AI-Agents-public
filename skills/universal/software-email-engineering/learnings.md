# software-email-engineering — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] Skill draft claimed Gmail/Microsoft bulk-sender DMARC minimum is p=quarantine; verified both providers' own docs require only p=none as the floor (p=quarantine/reject is best practice, not the compliance bar).
## Domain Knowledge

- [2026-07-11] BIMI now has a CMC path (no trademark needed) alongside VMC; Entrust exited BIMI certs and Google/Apple stopped trusting Entrust-issued certs from Nov 2024.
- [2026-07-11] New Outlook for Windows (Chromium/WebView2) is replacing classic Outlook's Word rendering engine — test both during the transition. **Corrected 2026-09-23:** the "default since Apr 2026 / Word-engine support ends Oct 2026" dates were wrong — Microsoft delayed the enterprise rollout (MC949965); look up current phase dates in Message Center instead of recording them here.
- [2026-07-11] Gmail (Nov 2025) and Outlook.com (May 2025) now reject non-compliant bulk mail instead of only spam-foldering it. **Corrected 2026-09-23:** Google's wording is "temporary and permanent rejections" (4xx and 5xx), not blanket 5xx; Outlook.com uses `550 5.7.515` and applies to consumer services only, requiring SPF and DKIM to both pass.
- [2026-09-23] DMARCbis (RFC 9989) removed `pct`/`rf`/`ri`; `t=y` applies the policy one level down; `np` came from RFC 9091, `psd` is new; mailbox domains whose users post to mailing lists SHOULD NOT publish `p=reject`.
## Open Questions

## Consolidated Principles

