# Nested Per-Feature CLAUDE.md — Worked Examples

Use this when you need to write a **scoped** memory file for one feature, package, or library inside a larger codebase, not the root file. The bullet density and gotcha-inline style here are tighter than what the root `AGENTS.md` should carry.

> **Provenance and warning.** The two examples below are real Apple internal CLAUDE.md files that leaked because they shipped inside the Apple Support iOS app bundle (v5.13, April 2026). They demonstrate excellent **content style** but also the **shipping antipattern** documented in [traps-and-antipatterns.md](traps-and-antipatterns.md): agent memory files must be excluded from production build artifacts (Xcode "Copy Bundle Resources", `.dockerignore`, npm `files` allowlist, etc.). Use them as a writing template — and audit your own builds with `unzip -l app.ipa | grep -iE 'claude|agents|cursor|goose'`.

## Example 1 — Feature subsystem (`Chat` directory)

```markdown
# Chat — Conversational Support (Juno AI + Live Agents)

- Uses **AsyncStream** for real-time updates, NOT Combine (unlike rest of app). Streams are recreated on each access; old ones are finished.
- Service providers are **actors** (not `@MainActor` classes) for thread-safe concurrent message handling.
- **Multi-backend via protocol:** `ChatViewModelServiceProvider` abstracts Juno AI (`SupportAssistantAPIProvider`), live agents (`ChatKitChatServiceProvider`), and dev mocks. View model doesn't know which backend is active.
- **Conditional compilation is heavy:** `#if JUNO_ENABLED`, `#if canImport(CCChatKit)`, `#if DEV_BUILD`. Some files nest these. Check xcconfig for enabled flags.
- **Three participant roles:** `.client` (user), `.agent` (live Apple Support), `.assistant` (AI). Route message handling per role.
- Messages are wrapped in `MessageGroup` (UUID container) to avoid SwiftUI ID collisions (rdar://164022273). Don't flatten.
- CCChatKit is callback-based; bridged to async/await via `Task` wrappers in `ChatFacadeServiceProvider`.
- Session persistence: Keychain for `ChatInfo` (reconnection), file cache in `CachesDirectory/TemporaryChatTranscripts/` for transcripts.
```

## Example 2 — Shared library (`SAComponents`)

```markdown
# SAComponents — Shared UI Component Library

- Components are purely UI — no business logic, no service dependencies.
- UIKit components use `UIContentConfiguration` protocol with preset factory methods (e.g., `.cell()`, `.callToActionProminent()`).
- SwiftUI components provide convenience modifiers on `View` (e.g., `platterBackground()`, `frame(square:)`).
- Presets live in `Presets/` as static factory methods on enums.
- Platform variants use `#if os(visionOS)` guards. iOS version conditionals use `#available`.
- DocC catalog in `SAComponents.docc/` with contributor guide. Update docs when adding components.
- Always include `#Preview {}` showing multiple states for new components.
```

## Why These Work

| Pattern | What to copy |
|---------|--------------|
| **One-line bullets** | Each rule fits on 1–3 visual lines. No paragraphs. ~7–10 bullets total. |
| **Bold lead phrase + colon** | `**Multi-backend via protocol:**` — gives the reader a scan-line; the agent gets a concept anchor. |
| **Backticked real identifiers** | Every type, file, flag, and path is a real symbol the agent can grep. No prose abstractions like "the chat service layer." |
| **Inline gotcha at end of line** | "Don't flatten" lives next to the rule that triggers it, not in a separate "Never do" list. Shorter, more relevant, harder to miss. |
| **Bug-tracker ID as authority** | `(rdar://164022273)` proves the rule isn't superstition. For OSS repos, use GitHub issue links. |
| **Contrast against repo default** | "AsyncStream … NOT Combine (unlike rest of app)" explicitly warns when this scope diverges from the root `AGENTS.md`. This is the *only* reason to nest a file. |
| **No platitudes** | Zero bullets like "follow Apple HIG" or "write clean code." Every line is a non-obvious, scope-specific fact. |

## Template

Distilled from the two examples above:

```markdown
# <Subsystem> — <one-line purpose>

- <Architecture pivot>: <what + why it differs from repo default if it does>.
- <Threading/async model>: <concrete primitive>, NOT <wrong-but-tempting alternative>.
- **<Concept name>:** `<protocol/type>` <abstracts/coordinates> <concrete implementations: `A`, `B`, `C`>.
- **<Build-flag situation>:** <#if list>. <Where to look>.
- <Important enum/role split>: `<.case1>` (<meaning>), `<.case2>` (<meaning>). <Routing rule>.
- <Subtle correctness rule that bit someone>: <reason> (<bug-tracker URL>). <One-word DON'T>.
- <Bridging note>: <legacy API> is <pattern>, bridged to <modern pattern> via <where>.
- <Persistence/state>: <what lives where>.
```

Aim for 7–10 bullets. If you need more, the file is probably trying to be a tutorial — split or push into the canonical docs.

## When to Use This vs. Root AGENTS.md

| Situation | Where the rule belongs |
|-----------|------------------------|
| Applies repo-wide | Root `AGENTS.md` |
| Applies to one subsystem AND contradicts/overrides a root convention | Nested `<subsystem>/CLAUDE.md` (or `AGENTS.md`) |
| Applies to one subsystem and the root file is silent on it | Nested file (so the root doesn't bloat with feature trivia) |
| Already obvious from reading the code | Don't write it — exception-file test |

The nested file inherits the root file. Only put **deltas, gotchas, and non-obvious scope-local facts** here. Do not repeat the build commands, test commands, or PR rules — those belong in the root.

## Build-Bundle Hygiene

Re-stating because the cost is high: the very files this page extracts content from leaked because someone added them to an Xcode target's "Copy Bundle Resources" phase. Before treating any of this as a template, confirm your build excludes agent memory files:

- **Xcode**: target → Build Phases → Copy Bundle Resources — no `*.md` from CLAUDE/AGENTS/cursor/goose.
- **Android Gradle**: `aaptOptions.ignoreAssetsPattern '!CLAUDE.md:!AGENTS.md:!.cursorrules'`.
- **Docker**: `.dockerignore` includes `CLAUDE.md`, `AGENTS.md`, `**/CLAUDE.md`, `**/AGENTS.md`.
- **npm**: explicit `files` allowlist in `package.json`, not `.npmignore` denylist.
- **Periodic audit**: `unzip -l app.ipa | grep -iE 'claude|agents|cursor|goose'` — should return nothing.

See [traps-and-antipatterns.md](traps-and-antipatterns.md) §"Common Anti-Patterns" for the full per-platform exclusion list.
