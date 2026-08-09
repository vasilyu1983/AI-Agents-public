# software-email-engineering — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] Skill draft claimed Gmail/Microsoft bulk-sender DMARC minimum is p=quarantine; verified both providers' own docs require only p=none as the floor (p=quarantine/reject is best practice, not the compliance bar).
## Domain Knowledge

- [2026-07-11] BIMI now has a CMC path (no trademark needed) alongside VMC; Entrust exited BIMI certs and Google/Apple stopped trusting Entrust-issued certs from Nov 2024.
- [2026-07-11] New Outlook for Windows (Chromium/WebView2) is replacing classic Outlook's Word rendering engine; default since Apr 2026, Word-engine support ends Oct 2026 — test both during the transition.
- [2026-07-11] Gmail (Nov 2025) and Outlook.com (May 2025) now hard-reject non-compliant bulk mail via SMTP 5xx instead of spam-foldering it.
## Open Questions

## Consolidated Principles

