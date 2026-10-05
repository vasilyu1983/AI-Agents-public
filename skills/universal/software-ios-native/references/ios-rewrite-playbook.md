# iOS Rewrite Playbook

Use this reference when the user is rewriting an existing app to modern native iOS. Treat this as the repo default migration shape, not as an Apple-mandated architecture.

## Rewrite stance

- Prefer an incremental rewrite over a big-bang replacement.
- Keep one active migration brief with:
  - target minimum OS
  - Swift / Xcode baseline
  - scope in and scope out
  - release blockers
  - parity exceptions accepted by the user
- Rewrite vertical slices, not disconnected utility layers.

## Safe slice order

1. App shell
   navigation, dependency wiring, environment, build settings, signing, launch path
2. Session and app state
   auth, onboarding gating, permissions, shared app state
3. Core feature slices
   one user-visible flow at a time
4. Integration surfaces
   push, deep links, background tasks, analytics, purchases, support SDKs
5. Release-only surfaces
   privacy, entitlements, metadata, QA matrix, archive and distribution checks

## Acceptance criteria per slice

- Builds in the intended configuration.
- Launches on the chosen simulator or device.
- The rewritten user flow works end-to-end for the slice.
- Targeted automated tests exist or were intentionally deferred with a reason.
- New privacy / entitlement / store review implications are recorded.
- Known parity gaps are explicit.

## Evidence bundle

Require a compact evidence bundle after each slice:

- build result
- run result
- screenshot or UI proof for user-facing changes
- targeted test result
- changed behavior summary
- residual risk and next slice

## Architectural defaults

Use these as repo defaults for low-ambiguity rewrites:

- SwiftUI-first UI
- UIKit interop only where needed
- Observation for new UI-facing state on iOS 17+
- structured concurrency for async work
- feature-oriented boundaries only when they reduce coupling; do not create module sprawl without a concrete need

## Avoid

- Rewriting multiple feature slices before one slice is fully validated.
- Migrating state model, navigation, persistence, and networking all at once without a feature boundary.
- Treating simulator-only proof as complete release proof.
- Hiding compatibility gaps behind “later cleanup” with no owner or end condition.
