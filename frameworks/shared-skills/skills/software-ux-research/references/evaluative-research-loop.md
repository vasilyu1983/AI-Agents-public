# Evaluative Research Loop for Prototype-Parity Polishing

Use this loop when product says "almost ideal" and needs fast, high-signal iteration.

## 1) Run a two-surface audit

Audit desktop and mobile separately for the same flow using:
- hierarchy and first-focus clarity,
- control consistency,
- duplication of meaning,
- whitespace efficiency,
- perceived compactness.

## 2) Compare prototype intent vs production reality

For each module, classify mismatch:
- `layout drift` (pairing/alignment/reflow),
- `density drift` (too much space/too many wrappers),
- `control drift` (mixed styles/duplicated actions),
- `content drift` (duplicate labels/text),
- `state drift` (loading/banner behavior unlike intended UX).

## 3) Prioritize by felt friction, not by component count

Prioritize issues users notice immediately:
1. Empty-space imbalance and broken rhythm.
2. Hidden or noisy critical actions.
3. Repetitive banners or repeated copy.
4. Non-compact disclosure patterns.
5. Mobile alignment and contrast misses.

## 4) Validate compaction with acceptance checks

- No persistent dead-right area after fold on desktop.
- Intentional 2-up pair modules remain paired.
- Expanded cards do not create opposite-column voids.
- Day selector and week control remain aligned and readable on mobile.

## 5) Banner and loading research guardrails

- Verify repeated-banners perception with quick evaluative checks; persistent banners quickly feel like clutter.
- Validate loading trust: users should recognize final layout from skeleton structure.
- Treat mismatched loading compositions as usability defects, not cosmetic debt.

## 6) Localization-readiness check in every evaluative pass

- Flag any hardcoded UI text immediately.
- Confirm all labels/CTAs/helper text map to locale keys.
- Ensure no mixed-language fragments on localized screens.

## 7) Fast iteration cadence (recommended)

1. Screenshot-based audit.
2. 5-issue max fix batch.
3. Re-check desktop + mobile side by side.
4. Update canonical principles doc.
5. Repeat until no high-severity visual/interaction drift remains.
