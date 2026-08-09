# iOS App Conveyor

Use this reference when the goal is to turn iOS development into a **repeatable production line** — shipping many apps where each new app is assembly, not reinvention. This is the "app factory" pattern. It assembles the agentic-tooling, CI, and stack references in this skill into one pipeline view and adds the multi-app factory layer (shared packages, one cert set, default-stack matrix) those don't cover individually.

Moving from a heavier web-first backend (e.g. Vercel + Supabase) to a leaner combo (CloudKit + Cloudflare) is a conveyor instinct: less per-app setup cost. The point of a conveyor is to make that low setup cost *systematic* across every app, not re-decided each time.

Verified June 2026.

## Table of Contents

- [What Makes a Conveyor](#what-makes-a-conveyor)
- [Pillar 1 — One Default Stack per App Class](#pillar-1--one-default-stack-per-app-class)
- [Pillar 2 — Shared Swift Packages (the reuse engine)](#pillar-2--shared-swift-packages-the-reuse-engine)
- [Pillar 3 — Multi-App CI/CD](#pillar-3--multi-app-cicd)
- [Pillar 4 — Agent-Driven Build Loop](#pillar-4--agent-driven-build-loop)
- [Trendy 2026 Stack Survey](#trendy-2026-stack-survey)
- [Is CloudKit + Cloudflare the Right Default?](#is-cloudkit--cloudflare-the-right-default)
- [Anti-Patterns](#anti-patterns)
- [Sources](#sources)

## What Makes a Conveyor

A conveyor is four pillars working together. Missing any one turns "shipping apps" back into "building each app":

1. **A default stack per app class** — so the backend decision is already made before the project starts.
2. **Shared Swift packages** — so auth, paywall, networking, design system are imported, not rewritten (reported 100–200+ hours saved per app).
3. **Multi-app CI/CD** — so build, sign, and TestFlight upload are one command across every app, with one shared cert set.
4. **An agent-driven build loop** — so SwiftUI/SwiftData/refactor work is delegated, with the three things agents can't do (pbxproj, signing, visual debug) routed around them.

The conveyor's throughput is set by its slowest manual step. Industrialize that step first.

## Pillar 1 — One Default Stack per App Class

Don't re-decide the backend each app. Bind a default to each class (see [../assets/scaffolds/app-class-blueprints.md](../assets/scaffolds/app-class-blueprints.md)):

| App class | Conveyor default | Why this is the default |
|---|---|---|
| Local-first CRUD / notes | CloudKit private + (Cloudflare Worker if paid) | Zero server, offline-first, free; the leanest line |
| AI wrapper | CloudKit + Cloudflare Worker (AI proxy) + on-device FM free tier | Worker keeps keys off-device; on-device AI is a free-tier with zero marginal cost |
| Content / feed / social | Supabase (Postgres) + CloudKit cache | Needs relational + cross-platform + auth at scale; CloudKit is the wrong core |
| Utility with IAP | CloudKit (or local) + StoreKit 2 | Often no server at all; simplest line |

Stack ladder and graduation logic: [starter-stacks-and-monetization.md](starter-stacks-and-monetization.md). The rule is *pick the default, deviate only on evidence* — a conveyor loses its speed the moment every app re-litigates the backend.

## Pillar 2 — Shared Swift Packages (the reuse engine)

This is the highest-leverage pillar. Maintain a **separate shared-packages repo** of internal SDKs so each app imports them via SPM instead of re-implementing — and so they stay discoverable without polluting every app's `Package.swift`.

Candidate packages (modularize by responsibility, not by app):

- `AppCore` — `EntitlementStore`, `PaywallGate`, `PushManager`, `Reachability` (the [scaffolds](../assets/scaffolds/) promoted to a versioned package).
- `DesignSystem` — tokens, the `motionSensitive()` modifier, shared list rows, the Liquid Glass `appChromeBackground` fallback (see `../../software-ios-design/`).
- `Networking` — typed client, the polymorphic-response decoding guard, auth header handling.
- `Persistence` — the CloudKit stack shape + migration plan scaffolding.

Rules that keep shared packages from becoming a liability:

- Version with semver tags; pin each app to a version, don't float `main`. A floating shared package turns one bug into N broken apps at once.
- Keep packages app-agnostic — no app-specific product IDs, copy, or branding inside. Those stay in the app target.
- Modular boundaries make each package independently testable; this is also what lets an agent work one package without loading the others.

## Pillar 3 — Multi-App CI/CD

The multi-app unlock is **one cert/profile set reused across every app**.

- **Fastlane + GitHub Actions** is the dominant 2026 indie pipeline: define `lanes` (test, beta, release) once, reuse across apps. **Fastlane Match** stores one set of certificates/provisioning profiles in a shared bucket and reuses them across all apps (same bucket + `MATCH_PASSWORD`) — instead of regenerating signing per app.
- **iOS CI still requires a real Mac in 2026** — no Linux VM or Docker runs Xcode's toolchain. The indie pattern is a remote Mac mini (M-series) as the build host, or GitHub Actions macOS runners; Xcode Cloud is the zero-infra alternative when you accept its constraints.
- **Make the project generated, not committed-as-pbxproj.** XcodeGen (or Tuist) regenerates `.xcodeproj` from a manifest, so adding files never desyncs target membership and agents never hand-edit `.pbxproj`. This is the decision that makes the rest of the conveyor automatable — see [agentic-ios-tooling.md](agentic-ios-tooling.md) and the XcodeGen rows in [../SKILL.md](../SKILL.md).
- **CI hook for generated files**: `ci_scripts/ci_post_clone.sh` synthesizes `.env`/Info.plist on a fresh clone — see [ios-release-and-compliance.md](ios-release-and-compliance.md). Any file the pbxproj references must be committed or regenerated CI-side, or Xcode Cloud breaks silently.
- **Mandatory from 2026-04-28**: every uploaded build must use the iOS 26 SDK (Xcode 26+). Pin the CI Xcode version to satisfy this and re-verify Liquid Glass chrome after the bump.

## Pillar 4 — Agent-Driven Build Loop

Three agent runtimes ship iOS code in 2026: **Claude Code CLI + MCP**, **Codex CLI + MCP**, and **Xcode's native Intelligence agents** (introduced Xcode 26.3, evolving each point release through 26.6 and into the Xcode 27 beta line from WWDC26). Structured access comes from two MCP servers: **XcodeBuildMCP (~59 tools)** and Apple's **`xcrun mcpbridge` (~20 tools)** — builds, tests, simulators, debugging, Xcode Preview capture.

- **Delegate to agents**: SwiftUI views, SwiftData models, refactors, build-error diagnosis, and the proof loop (build → install → launch → screenshot → fix). See [xcodebuildmcp-workflows.md](xcodebuildmcp-workflows.md), [codex-claude-ios-workflows.md](codex-claude-ios-workflows.md), and [runtime-proof-and-prompts.md](runtime-proof-and-prompts.md).
- **Route around agents** (the three failure modes): `.pbxproj` modification (solved by XcodeGen/Tuist regeneration), code signing (solved by Fastlane Match — a deterministic step, not a judgment call), and visual debugging (a human verifies screenshots; the agent captures them).
- **The local-dev launcher pair** (`scripts/run-local-ios-dev.sh` + `stop`) with its localhost guards keeps the agent loop from silently building against production — see the SKILL.md launcher row. This is conveyor safety infrastructure.

## Trendy 2026 Stack Survey

The honest 2026 landscape — there is no universal winner, only a best fit per app class:

| Stack | Strength | Best app class | Watch out |
|---|---|---|---|
| CloudKit + Cloudflare | Free private sync + cheap edge server; Apple-native | Private CRUD, AI wrappers | No cross-platform; iOS 26 sync regression (workarounds in [swiftdata-core.md](swiftdata-core.md)) |
| Firebase | Most polished mobile SDKs; offline sync, push, crash, analytics in one box | Mobile-first consumer apps wanting max velocity | Real lock-in; NoSQL model |
| Supabase | Postgres + auth + storage + realtime + pgvector, OSS | Content/feed/social, cross-platform, AI-RAG | More setup than CloudKit; you run more |
| Convex | Reactive TS backend, functions-as-backend, no API layer | Real-time TS-heavy apps with a web companion | Newer; TS mental model, not tables |
| Neon | Serverless Postgres with branching | When you want Postgres + per-PR DB branches | A database, not a full BaaS |

The 2026 consensus: **Firebase for mobile velocity, Supabase for Postgres control, Convex for reactive TS, CloudKit+Cloudflare for private Apple-native + edge.** A conveyor picks 2–3 of these (mapped to app classes), not all five.

## Is CloudKit + Cloudflare the Right Default?

For a conveyor whose typical app is a **private, single-platform, Apple-native app with light monetization**, yes — it is an excellent default: zero backend cost at Tier 0, an offline-first store users already trust, and a cheap edge Worker for the server-side jobs CloudKit can't do. Your move off Vercel + Supabase removed per-app hosting and Postgres-ops overhead you weren't using.

It stops being the right default the moment a class needs:

- **Cross-platform or a web client** → Supabase or Firebase (CloudKit is Apple-only).
- **Shared/public/social data** → Supabase (CloudKit's private-by-design model fights you).
- **Maximum mobile-SDK velocity with push+crash+analytics bundled** → Firebase.
- **Real-time reactive data with a TS team** → Convex.

So the conveyor answer is not "one default" but **a default per app class** (Pillar 1): CloudKit + Cloudflare for private/AI-wrapper apps, Supabase for social/content, with Firebase as the velocity option. Keep the line for each class fixed; switch lines by class, never per app.

## Anti-Patterns

- **Re-deciding the backend every app.** Kills conveyor throughput. Bind defaults to app classes once.
- **Floating shared packages on `main`.** One upstream bug breaks every app simultaneously. Pin semver versions per app.
- **App-specific code inside shared packages.** Branding, product IDs, and copy leak the factory into the product. Keep packages app-agnostic.
- **Per-app signing.** Regenerating certs/profiles per app is wasted manual work; use one Match set across all apps.
- **Committing `.xcodeproj` and letting agents edit it.** `.pbxproj` is the #1 agent failure mode. Generate the project from a manifest instead.
- **Trying to run iOS CI on Linux/Docker.** Xcode's toolchain needs a real Mac in 2026. Plan for a Mac build host.
- **Letting the agent build against production.** Use the guarded local-dev launcher pair; a silent prod build in the loop is a data-safety incident waiting to happen.

## Sources

- The Swift Kit / Swift Starter Kits / SwiftShip — production SwiftUI boilerplates (100–200+ hrs/app saved)
- Nimble: [Modularizing iOS with SwiftUI + SPM](https://nimblehq.co/blog/modern-approach-modularize-ios-swiftui-spm)
- Runway: [iOS CI/CD with Fastlane + GitHub Actions](https://www.runway.team/blog/how-to-set-up-a-ci-cd-pipeline-for-your-ios-app-fastlane-github-actions)
- Apple: [Xcode 26.3 unlocks agentic coding](https://www.apple.com/newsroom/2026/02/xcode-26-point-3-unlocks-the-power-of-agentic-coding/)
- [Building iOS Apps with AI Agents — Practitioner's Guide](https://blakecrosley.com/guides/ios-agent-development) (3 runtimes; XcodeBuildMCP + xcrun mcpbridge)
- Encore: [Firebase alternatives 2026](https://encore.dev/articles/firebase-alternatives) · Cadence: [Convex vs Supabase vs Firebase 2026](https://cadence.withremote.ai/blog/convex-vs-supabase-vs-firebase)

Follow the cross-links into the owning references for implementation depth; this file is the assembly diagram, not the parts list.
