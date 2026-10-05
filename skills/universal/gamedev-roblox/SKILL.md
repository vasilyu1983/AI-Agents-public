---
name: gamedev-roblox
description: "Creates Roblox experiences from empty Studio place to published world. Use when starting, building, validating, or shipping a Roblox game."
compatibility: Portable core. Works on Claude Code and Codex. Roblox platform facts are dated and drift; verify volatile numbers against current primary sources.
version: "1.2"
last_validated: 2026-07-11
---

# Roblox World Creation

Use this skill to take a Roblox experience from empty Studio place to a published, retainable world. It covers the durable build spine (greybox → first playable → detail → ship) and fences the volatile platform layer (rates, fees, limits, discovery ranking, publishing rules, renamed APIs) behind lookup steps. Roblox changes that layer without warning — the discovery algorithm, the DataStore budget model, and UGC publishing rules have each changed materially within a year — so look up the current state on create.roblox.com and in DevForum announcements before relying on any of it.

## Quick Reference

| Stage | Read or Run | Durable default |
|-------|-------------|----------------------------|
| **Setup & toolchain** | `references/setup-and-toolchain.md` | Studio + **Rojo + Rokit + Wally** for git-native teams; **Script Sync** (Roblox-native, Team-Create compatible; check its current release status and known issues on the DevForum) for Studio-led collaboration; partially managed Rojo can keep world building in Team Create; `default.project.json` defines the DataModel tree |
| **Language & architecture** | `references/luau-and-architecture.md` | `--!strict` Luau; **`task.wait/spawn/defer`** never `wait()/spawn()`; server-authoritative; RemoteEvent + `UnreliableRemoteEvent` for high-frequency; **ProfileStore** for player data |
| **Build the world** | `references/world-building.md` | Greybox in Parts first; 1 stud ≈ 0.28 m; enable `StreamingEnabled` in Studio; **Unified Lighting** `LightingStyle = Realistic` + `PrioritizeLightingQuality` (the old `Technology` enum is deprecated) |
| **Performance & traps** | `references/performance-and-traps.md` | Anchor static parts; opaque geometry by default; profile overlapping transparency; disconnect every connection; ProfileStore (atomic update + lease lock) or hand-rolled `UpdateAsync` + leased lock, never both, plus `BindToClose`; idempotent `ProcessReceipt`; bounded waits plus stream-out/re-entry handling in LocalScripts |
| **Discovery, economy, policy** | `references/discovery-economy-policy.md` | Design for first-session clarity and mid-game retention, not lifetime totals — look up the current RFY signal definitions before tuning; complete the **maturity questionnaire**; gate paid random items per player via `PolicyService`; design sinks for every source; never trust the client for economy |
| **AI-assisted creation** | `references/setup-and-toolchain.md#ai-assisted-creation` | Studio **Assistant**, the material and texture generators, **Code Assist**, and a Studio **MCP server** for external LLMs — check each tool's current release stage (Beta vs GA) and limits in the Creator Hub docs before depending on it |

## World Creation Workflow

The durable spine. Each step names its verification check inline — do not advance from a state you cannot describe back.

1. **Scope the world to a testable first playable** → verify: one sentence — "a player spawns, can perform the core verb, and has a reason to return tomorrow." If you can't write it, stop and get it.
2. **Set up the toolchain and place structure** → verify: `rojo serve` syncs a filesystem edit into Studio; with Script Sync, test both directions for supported scripts; `default.project.json` maps `src/` to the right services. See `references/setup-and-toolchain.md`.
3. **Greybox the world in Parts only** — no meshes, textures, or scripts → verify: you can walk the whole space, sightlines and player flow read clearly at player scale (1 stud ≈ 0.28 m). See `references/world-building.md`.
4. **Stand up the architecture skeleton** — server-authoritative state, one RemoteEvent path, ProfileStore-backed save, CollectionService tags for repeated objects → verify: a value changed on the server replicates; a client-only currency value does **not**; client-owned physics is a replication exception, so validate movement and gameplay-critical physics on the server. See `references/luau-and-architecture.md`.
5. **Reach First Playable** — working spawn/respawn, one lighting pass, the core loop is playable end to end → verify: Team Test with a second client; the loop is completable without programmer intervention.
6. **Detail pass** — modular kits replace greybox, PBR/SurfaceAppearance, atmosphere, sound zones → verify: part count and draw calls still inside budget on a real low-end Android, not just the Studio emulator. See `references/world-building.md` and `references/performance-and-traps.md`.
7. **Harden** — rate-limit and type-validate every `OnServerEvent`; serialize economy remotes; disconnect every connection; `BindToClose` save; one lease lock on player data (ProfileStore's, or a hand-rolled one, never both); idempotent `ProcessReceipt`; `PolicyService` gate on paid random items → verify: walk `references/performance-and-traps.md` Known Traps as a checklist; MicroProfiler shows no runaway frame peaks.
8. **Soft-launch under real concurrency** — release to a capped audience (private server, limited region, or throttled ad spend) before wide release → verify: choose a capped load from expected server occupancy and launch concurrency; measure server CPU, join bursts, remote traffic, and DataStore throttling across servers. Look up current request-type experience limits, server limits, and shared Open Cloud usage in the DataStore limits docs. `GetRequestBudgetForRequestType()` reports the current server’s available requests, not the experience’s remaining pool. Fix observed failures before expanding the audience.
9. **Ship and tune for discovery** — complete the maturity questionnaire (mandatory), set access and game settings, publish, then design the FTUE and loops around the RFY signals → verify: experience is rated — look up the current restriction on unrated experiences in the maturity-questionnaire docs (it has tightened from hidden-in-search to blocking play for users; you can still playtest unrated in Studio); first-session core-loop comprehension is real. See `references/discovery-economy-policy.md`.

## Patterns (durable)

- **Server is the single source of truth.** Clients request; the server decides. FilteringEnabled cannot be turned off — design as if every client is hostile.
- **`task` library, always.** `task.wait/spawn/delay/defer` and `signal:Once()`. The legacy `wait()/spawn()/delay()` globals are deprecated and drift under load.
- **Set properties before parenting.** `Instance.new("Part")`, configure, then set `.Parent` last — avoid replicating intermediate property changes.
- **Stream the world.** Enable `StreamingEnabled` in Studio; use bounded waits for missing Workspace objects, handle timeout `nil`, and clean up/rebind when objects stream out and back in; keep `ReplicatedStorage`/`ReplicatedFirst` lean (they never stream).
- **Atomic, lease-locked saves — one mechanism, not two.** Use ProfileStore, which provides the atomic update and the session lease lock. Hand-roll `UpdateAsync` (never `SetAsync` for shared keys) plus a leased lock keyed on `game.JobId` only when not using ProfileStore. Never do both on the same data. Either way, flush in `BindToClose` and save on cadence and on critical events, not on every stat change.
- **One script for many things.** CollectionService tags + a single manager script for repeated objects (doors, spawns, traps), not a Script per instance.
- **Client does pixels, server does truth — but "truth" means adversarial state, not everything.** Validate what a cheater profits from (currency, damage, hit-reg, item grants); leave non-adversarial state (camera shake, footstep particles, ragdoll poses) client-authoritative. Over-validating cosmetic state burns server CPU for zero security benefit. See `references/luau-and-architecture.md`.
- **Network ownership is the physics-feel lever.** `part:SetNetworkOwner(player)` makes their own vehicle/tool physics simulate locally with more responsive input; `SetNetworkOwner(nil)` forces server ownership for contested/exploitable physics. This — not RemoteEvents — is why "my car lags for the driver."
- **Serialize economy remotes.** Two fires of a spend/grant remote can land in one frame before the first write commits (the dupe race). Process economy-affecting remotes through a per-player serial queue, not independent handlers.
- **Design for retention signals, not raw volume.** Recent RFY versions score early and later retention windows separately rather than lifetime totals (look up the current window definitions before tuning) — a strong new experience can outrank a large declining one, and a strong first session with no mid-game hook shows up as a weak later window instead of being averaged away.
- **Every currency/item source needs a sink.** Before shipping a new way to earn, decide what removes it from the economy — otherwise you get inflation and an economy that only rewards early adopters. See `references/discovery-economy-policy.md#economy-design-judgment-sinks-sources-and-exploit-economics`.
- **Roblox isn't always the right call.** Sexual/gambling content, full payment-stack control, frame-perfect competitive netcode, non-Roblox-client distribution, and adult-first products fit poorly on this platform — recognize the mismatch before scoping the build. See `references/discovery-economy-policy.md#when-roblox-is-the-wrong-platform`.

## Anti-Patterns

- Changing currency, health, or inventory in a LocalScript and expecting the server (or other players) to see it.
- Trusting numeric arguments from `OnServerEvent` for economy or stat changes instead of computing on authoritative server state.
- `SetAsync` on a shared key from multiple servers (race → data loss); no `BindToClose` (lose the last autosave on shutdown).
- Heavy overlapping transparency without profiling, or `RenderFidelity = Precise` on background geometry; unanchored static parts; per-instance Scripts where one tagged manager would do.
- Connecting events per-respawn without disconnecting (the most common silent memory leak); busy-wait `while ... do wait() end` loops.
- Setting the deprecated `Lighting.Technology` enum in a new project instead of `LightingStyle` + `PrioritizeLightingQuality`.
- Shipping unrated (skipping the maturity questionnaire) → blocked or hidden for users under the current rule (it has only tightened; look it up), and absent from top charts.
- Quoting a DevEx rate, fee, part budget, or DataStore limit from memory without re-verifying — every one of these has changed; look up the current value.

## Known Traps

**Remote mutation gate.**

For every `RemoteEvent` or `RemoteFunction` that can change inventory, currency, progression, trades, or purchases, write the server-owned invariant beside the handler. Validate instance ancestry, types, bounds, entitlement, and current server state; rate-limit by player and action; then perform the mutation once under an idempotency key or atomic update. A client request is an intent, never evidence that the action is allowed.

- **`wait()` drift** — legacy scheduler resumes on ~1/30s minimum and accumulates drift; use `task.wait`.
- **Replication timing** — a Workspace object that exists on the server may not have replicated/streamed to a given client yet; use bounded waits and handle `nil`; later stream-out needs removal handling and re-entry binding too.
- **Humanoid race** — `Humanoid`/`HumanoidRootPart` are not all present the instant `CharacterAdded` fires; `:WaitForChild` them.
- **DataStore throttling** — experience-level request budgets are shared across game servers and Open Cloud, while each server also has a configurable contribution limit. A burst can exhaust the experience budget unless servers are bounded deliberately. Inspect the current server’s `GetRequestBudgetForRequestType()`; check current experience/request-type limits and `SetRateLimitForRequestType()` semantics in the official limits docs, and wrap operations in `pcall` with structured logging.
- **`RemoteFunction:InvokeClient()` from the server** — a malicious client can yield forever and hang the thread; never call it.
- **Emulator ≠ device** — Studio's device emulator tests layout only, not CPU/GPU; test CPU, GPU, and memory on a real device representing the lowest supported hardware.
- **New Type Solver footguns** — the new type solver has had open issues (check the Luau release notes and DevForum for whether they are fixed): stale `Parent`/`Model` type narrowing after reparenting or reassignment, and high Studio memory use. If strict-typed code reports impossible type errors after moving instances, suspect the solver, not your code.
- **Script Sync edge cases** — Script Sync has had reported "ghost instances" in Team Create and silently skips scripts nested under non-Folder/non-Script ancestors. Confirm every script actually round-trips; don't assume a clean sync.
- **Developer-product receipts (`ProcessReceipt`)** — the most common way a game loses money or dupes items. When using `ProcessReceipt`, assign one central dispatcher in each server, shared by all its developer products; another assignment in that server replaces it. Use durable receipt deduplication across servers. Make it idempotent: commit each grant and its `PurchaseId` together in the player's persisted profile and return `PurchaseGranted` immediately for one already recorded. Return `PurchaseGranted` only after the grant and the `PurchaseId` are saved; return `NotProcessedYet` on any error, a failed save, or when the player is no longer in the server, so Roblox retries later.
- **Paid random items** — before shipping anything bought with Robux or real money whose contents are random (loot boxes, gacha, random packs), check `PolicyService:GetPolicyInfoForPlayerAsync(player)` on the server for each player and block the purchase where paid random items are restricted, and disclose odds as current Roblox policy requires. The field names, affected regions, and disclosure rule are volatile: look them up in the PolicyService and monetization-policy docs before shipping.

## Frameworks (status drifts — check repo activity and releases before adopting)

| Need | Pick | Status |
|------|------|--------|
| Player data persistence | **ProfileStore** | Community standard; successor to the deprecated ProfileService |
| Tag/component architecture | **CollectionService** (optionally **Stamp** wrapper) | Built-in; idiomatic |
| Typed networking | **Jolt** (community) or **ByteNet** | Community options; check whether Roblox now ships an official typed networking API before adding one |
| ECS | **Matter** (`matter-ecs`) | Maintenance has been in doubt; do not adopt for new production ECS without confirming recent activity on the canonical or fork repos |
| Module framework | Modular OOP, or ECS if needed | **Knit** has been declared unmaintained — confirm repo status; do not start new projects on an unmaintained framework |
| Build automation / CI | **Lune** + **Wally** + **Rokit** | Git-native production stack |

## Navigation

Resources:

- [references/setup-and-toolchain.md](references/setup-and-toolchain.md) — Studio, Rojo/Script Sync/Azul, Rokit/Wally/Lune, project structure, and AI-assisted creation
- [references/luau-and-architecture.md](references/luau-and-architecture.md) — Luau (strict types, task, native, buffer), client-server model, network ownership, client-vs-server authority judgment, remotes + anti-exploit (dupe races, speed hacks), data persistence (ProfileStore lease traps, DataStore budget bursts, schema migration), Parallel Luau/Actors, MessagingService, module patterns
- [references/world-building.md](references/world-building.md) — Scale, greyboxing, modular kits, Unified Lighting, terrain/mesh/PBR, sound, streaming, publishing and testing
- [references/performance-and-traps.md](references/performance-and-traps.md) — Performance budgets, profiling, memory-leak patterns, and the full Known Traps catalog with fixes
- [references/discovery-economy-policy.md](references/discovery-economy-policy.md) — RFY discovery signals, monetization mix, retention/FTUE design, content maturity and safety policy, UGC economy
- [data/sources.json](data/sources.json) — Primary sources to verify volatile facts against

Related skills:

- [../software-mobile/SKILL.md](../software-mobile/SKILL.md) — Mobile-platform constraints and store flows
- [../software-performance/SKILL.md](../software-performance/SKILL.md) — General performance profiling discipline
- [../software-ui-ux-design/SKILL.md](../software-ui-ux-design/SKILL.md) — Onboarding and flow design that transfers to FTUE

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

## Version Drift Notes

- Roblox platform facts are **high-drift**. Treat every rate, fee, percentage, numeric limit, maturity age, and recently renamed API as volatile and verify against current primary sources (create.roblox.com, devforum.roblox.com, luau.org, about.roblox.com) before quoting.
- The references separate **DURABLE** principles (build order, server authority, save discipline) from **VOLATILE** facts (budgets, rates, API names) and replace the volatile ones with lookup steps or `verify` labels rather than dated values.
- Items announced on the roadmap but not confirmed shipped (e.g. CSG-on-meshes, enhanced voxel terrain, Android native codegen) are marked as such — confirm shipping status before depending on them.
- If web access is unavailable, state the limitation and mark any volatile platform claim as unverified rather than asserting it as current.
