# Nested Per-Feature CLAUDE.md — Worked Example

Use this when you need to write a **scoped** memory file for one feature, package, or library inside a larger codebase, not the root file. The bullet density and gotcha-inline style here are tighter than what the root `AGENTS.md` should carry.

The example below is synthetic: an invented `payments/sync/` subsystem in an invented mobile app. Copy the shape, not the content.

## Example: `payments/sync/CLAUDE.md`

```markdown
# Payment Sync — offline queue that replays card payments when the device reconnects

- **Queue, not direct calls:** every write goes through `PaymentQueue.enqueue(_:)`. Never call `PaymentsAPI` from a view model; the queue owns retries and ordering.
- **Async model:** structured concurrency with `AsyncStream`, NOT callbacks (unlike the rest of the app). Do not bridge back to completion handlers inside this folder.
- **Idempotency key per attempt group:** `PaymentIntent.idempotencyKey` is created once at enqueue time and reused on every retry. Regenerating it double-charges (issue #412).
- **Two stores:** `PendingStore` (encrypted, survives app kill) and `ReceiptCache` (memory only). Only `PendingStore` is the source of truth after a crash.
- **Build flags:** `#if SANDBOX_PAYMENTS` swaps `LivePaymentsAPI` for `FakePaymentsAPI`. Tests must set the flag in the test target, not in code.
- **Status enum routing:** `.queued` and `.retrying` show a spinner; `.failedPermanent` must surface the error copy from `PaymentErrors.strings`. Don't map `.failedPermanent` to a retry.
- **Legacy bridge:** `LegacyCheckoutAdapter` converts the old delegate API to the queue. Delete it only after `checkout/` stops importing it.
```

## Why This Works

| Pattern | What to copy |
|---------|--------------|
| **One-line bullets** | Each rule fits on 1–3 visual lines. No paragraphs. ~7–10 bullets total. |
| **Bold lead phrase + colon** | `**Queue, not direct calls:**` gives the reader a scan-line and the agent a concept anchor. |
| **Backticked real identifiers** | Every type, file, flag, and path is a real symbol the agent can grep. No prose abstractions like "the payment layer." |
| **Inline gotcha at end of line** | "Don't map `.failedPermanent` to a retry" lives next to the rule that triggers it, not in a separate "Never do" list. Shorter, more relevant, harder to miss. |
| **Issue ID as authority** | `(issue #412)` shows the rule came from a real incident, not superstition. Use your tracker's link format. |
| **Contrast against repo default** | "`AsyncStream`, NOT callbacks (unlike the rest of the app)" warns when this scope diverges from the root `AGENTS.md`. This is the main reason to nest a file. |
| **No platitudes** | Zero bullets like "follow platform guidelines" or "write clean code." Every line is a non-obvious, scope-specific fact. |

## Template

```markdown
# <Subsystem> — <one-line purpose>

- <Architecture pivot>: <what + why it differs from repo default if it does>.
- <Threading/async model>: <concrete primitive>, NOT <wrong-but-tempting alternative>.
- **<Concept name>:** `<protocol/type>` <abstracts/coordinates> <concrete implementations: `A`, `B`, `C`>.
- **<Build-flag situation>:** <#if list>. <Where to look>.
- <Important enum/role split>: `<.case1>` (<meaning>), `<.case2>` (<meaning>). <Routing rule>.
- <Subtle correctness rule that bit someone>: <reason> (<issue link>). <One-word DON'T>.
- <Bridging note>: <legacy API> is <pattern>, bridged to <modern pattern> via <where>.
- <Persistence/state>: <what lives where>.
```

Aim for 7–10 bullets. If you need more, the file is probably trying to be a tutorial — split it or push it into the canonical docs.

## When to Use This vs. Root AGENTS.md

| Situation | Where the rule belongs |
|-----------|------------------------|
| Applies repo-wide | Root `AGENTS.md` |
| Applies to one subsystem AND contradicts a root convention | Nested `<subsystem>/CLAUDE.md` (or `AGENTS.md`) |
| Applies to one subsystem and the root file is silent on it | Nested file (so the root doesn't bloat with feature trivia) |
| Already obvious from reading the code | Don't write it — exception-file test |

Nested files are added to the root file's context, not substituted for it: both are loaded and concatenated. Put only **deltas, gotchas, and non-obvious scope-local facts** here. Do not repeat the build commands, test commands, or PR rules — those belong in the root. When a nested line contradicts the root, say so explicitly ("unlike the rest of the app") so the model is not left to guess which instruction wins.

## Build-Bundle Hygiene

Scoped memory files sit next to source code, so they are easy to ship by accident. They expose internal architecture, open bugs, and tracker IDs. Before relying on nested files, confirm your build excludes them:

- **Xcode**: target → Build Phases → Copy Bundle Resources — no `*.md` from CLAUDE/AGENTS/cursor/goose.
- **Android Gradle**: `aaptOptions.ignoreAssetsPattern '!CLAUDE.md:!AGENTS.md:!.cursorrules'`.
- **Docker**: `.dockerignore` includes `CLAUDE.md`, `AGENTS.md`, `**/CLAUDE.md`, `**/AGENTS.md`.
- **npm**: explicit `files` allowlist in `package.json`, not an `.npmignore` denylist.
- **Periodic audit**: `unzip -l app.ipa | grep -iE 'claude|agents|cursor|goose'` — should return nothing.

See [traps-and-antipatterns.md](traps-and-antipatterns.md) §"Common Anti-Patterns" for the full per-platform exclusion list.
