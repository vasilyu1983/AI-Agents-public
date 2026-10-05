# Frontend Code Review Checklist

Use this template when reviewing frontend PRs (React/Next.js/Vue/Angular/TypeScript/JavaScript).

## Core

### Standards

- Clean code standard (cite `CC-*` IDs): [../../../software-clean-code-standard/references/clean-code-standard.md](../../../software-clean-code-standard/references/clean-code-standard.md)
- Shared performance + accessibility checklist: [../../../software-clean-code-standard/assets/checklists/frontend-performance-a11y-checklist.md](../../../software-clean-code-standard/assets/checklists/frontend-performance-a11y-checklist.md)
- Shared UX design review checklist (optional): [../../../software-clean-code-standard/assets/checklists/ux-design-review-checklist.md](../../../software-clean-code-standard/assets/checklists/ux-design-review-checklist.md)

### Intent & Scope

- [ ] PR description states what/why/scope; include screenshots/video for UI changes.
- [ ] Diff matches intent; unrelated refactors are split or explicitly justified.

### UX Correctness

- [ ] Visual output matches design system/tokens; responsive across breakpoints.
- [ ] Loading/empty/error states are correct and non-jarring.
- [ ] Primary flows remain intuitive; navigation and state changes avoid surprises.

### Accessibility

- [ ] Semantic HTML used; headings/landmarks are logical; forms have labels and accessible errors.
- [ ] Keyboard navigation and focus management work for all interactive flows.
- [ ] Touch targets meet WCAG 2.2 SC 2.5.8 target size (24x24 CSS px; exceptions apply) https://www.w3.org/TR/WCAG22/#target-size-minimum

### Performance

- [ ] Untrusted or large inputs are bounded (pagination/virtualization/limits) (cite `CC-PERF-01`).
- [ ] Obvious performance hazards avoided (e.g., N+1 fetching, O(n²) rendering patterns) (cite `CC-PERF-02`).
- [ ] Rendering avoids unnecessary expensive work on input; code splitting used where appropriate.

### Security & Privacy

- [ ] Untrusted content is escaped/sanitized; no unsafe interpolation into HTML (cite `CC-SEC-08`).
- [ ] Secrets and sensitive data are not shipped to clients or logged (cite `CC-SEC-03`, `CC-OBS-02`).
- [ ] Auth/session handling follows product policy (cookie vs storage) and CSRF is handled when needed.

### Reliability & Operability

- [ ] Error boundaries or equivalent fault isolation exists for risky UI paths.
- [ ] Async flows have explicit timeout/cancellation where supported; failures are actionable (cite `CC-ERR-01`, `CC-ERR-04`).
- [ ] Critical UX paths emit usable telemetry (logs/metrics/traces as applicable) (cite `CC-OBS-03`).

### Tests

- [ ] New behavior has tests; bug fixes include regression tests (cite `CC-TST-01`).
- [ ] Tests match risk (unit/integration/e2e) rather than blanket thresholds (cite `CC-TST-04`).

## Optional: AI / Automation

- [ ] Lint/typecheck/tests are green; automation findings are mapped to `CC-*` IDs where possible.
- [ ] Core Web Vitals and bundle-size regressions checked (https://web.dev/vitals/).
- [ ] If shipping AI UX: cancel/stop, streaming state, safe fallbacks, and privacy boundaries are explicit [Inference].
