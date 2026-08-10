# software-ui-ux-design — Learnings

## Patterns That Work

- [2026-08-09] When a site's thesis is 'receipts', diff its published numbers against the owner's source-of-truth profile before auditing layout: ym8.co.uk shipped a metric its own provenance audit had quarantined, via meta + JSON-LD + llms.txt.
## Mistakes to Avoid

- [2026-08-09] A literal U+002D hyphen in a display headline is always a soft-break opportunity even under hyphens:manual — ym8's 68px hero broke as 'I Re-/architect Signal.' Fix: U+2011. text-wrap:balance does not prevent it.
- [2026-08-09] Print conventions ported to scroll: CSS column-count:2 on a 1119px block in a 1000px viewport forces a full-viewport scroll BACK UP to start column two. Measure column height vs viewport before accepting multi-column body text.
- [2026-07-10] Render the money surface under every billing-toggle state: cosmic-landing's CTA said 'Start for £0.99' (monthly intro) while Annual £39.99 was the selected default. Also diff hero copy across locales — ar carried stale positioning.
- [2026-07-10] 2026-07-10: Tailwind space-x-*/ml-* silently break RTL (use gap-x-*/ms-*); Latin-only brand fonts (Cormorant/Inter) leave ar/zh headings on system fallback.
- [2026-07-10] 2026-07-10: Audit i18n sites by rendering pages, not reading code: message-schema drift vs component keys rendered raw i18n keys on the money page in all locales while every JSON file looked valid.
## Domain Knowledge

- [2026-07-11] DTCG 2025.10 reached first-stable status Oct 2025 (still a W3C Community Group report, not a Recommendation); EN 301 549 V4 (WCAG 2.2 AA) drafted but not yet OJ-cited, so 2.1 AA stays the EAA legal floor.
- [2026-07-11] ADA Title II WCAG 2.1 AA deadlines extended one year (IFR eff. 20 Apr 2026): large entities to 26 Apr 2027, small/special districts to 26 Apr 2028 — always re-check DOJ dates.
## Open Questions

## Consolidated Principles

