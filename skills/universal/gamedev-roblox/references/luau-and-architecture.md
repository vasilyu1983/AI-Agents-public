# Luau & Architecture

The language idioms and client-server architecture for a new world. Patterns here are durable; specific solver-migration timelines and platform restrictions are dated.

## Table of Contents

- [Luau Language State](#luau-language-state)
- [The task Library (replace wait/spawn/delay)](#the-task-library-replace-waitspawndelay)
- [Type Checking](#type-checking)
- [Native Code Generation and buffer](#native-code-generation-and-buffer)
- [Client-Server Model](#client-server-model)
- [Remotes](#remotes)
- [Data Persistence](#data-persistence)
- [Architecture Patterns](#architecture-patterns)
- [Module Frameworks](#module-frameworks)
- [Skeleton Code](#skeleton-code)

## Luau Language State

Luau is statically-typed, gradually-typed Lua. Baseline for new code:

- Write new code with type annotations and a strictness mode declared at the top of the file.
- Prefer the `task` library, `vector` built-in, and `buffer` for binary data.
- Luau has been migrating to a **New Type Solver**, with different defaults for `--!strict` and for `--!nonstrict`/`--!nocheck` files during the migration and an opt-in workspace property (`UseNewLuauTypeSolver`). Look up the current solver defaults and migration status in the Luau release notes before diagnosing type errors or setting the property.

## The task Library (replace wait/spawn/delay)

`wait()`, `spawn()`, `delay()` are **deprecated**. The legacy scheduler resumes on a ~1/30s minimum and accumulates drift under load. Always use:

```lua
task.wait(seconds)        -- accurate yield
task.spawn(fn)            -- fire-and-forget new thread
task.delay(seconds, fn)   -- deferred execution
task.defer(fn)            -- run at end of current resumption cycle
task.cancel(thread)       -- cancel a scheduled thread
```

For single-fire event handling use `signal:Once(fn)` (auto-disconnects) instead of a manual connect+disconnect. Replace busy-wait `while not ready do task.wait() end` with event-driven patterns (`.Changed`, `GetPropertyChangedSignal`, a `BindableEvent`).

## Type Checking

Declare strictness at the top of each script:

- `--!strict` — full type checking; recommended for new modules.
- `--!nonstrict` — reports only definite runtime errors; gentler default.
- `--!nocheck` — off.

Annotate function signatures and table shapes. Precise number-type annotations also feed native code generation (below).

## Native Code Generation and buffer

- `--!native` at the top of a script compiles its functions to native machine code. GA on servers and in Studio. Best for numeric/math-heavy loops (intersection tests, custom pathfinding); **does not help** scripts that mostly call engine APIs. Profile with the Script Profiler before adding it.
- Platform note: check whether native codegen runs on each client platform you target (Android client support has lagged servers and Studio); do not assume mobile native speedups.
- `buffer` is a built-in type for compact binary data (with `buffer.readbits`/`writebits`). Pairs with native codegen and is the tool for dense custom replication payloads.

## Client-Server Model

Server-authoritative, always. FilteringEnabled is permanently on and cannot be disabled.

| Context | Runs where | Trust |
|---------|-----------|-------|
| `Script` | Depends on `RunContext` and location; check the Script API | Server execution trusted; client execution untrusted |
| `LocalScript` | Client | **Untrusted** — exploitable |
| `ModuleScript` | In the context of its requirer | Inherits caller's trust |

Implications:
- Ordinary property/instance edits in a LocalScript are client-only; changing a local currency value does not change server-owned currency. Client-owned physics is an exception: its simulation can replicate, so the server must validate gameplay-critical movement and interactions.
- Cheaters can run LocalScript-equivalent code via executors. The server must validate everything that affects shared state.
- **Client code is fully readable.** Exploiters decompile LocalScript bytecode trivially — every constant you ship (drop rates, prices, `--!strict` types, "secret" thresholds) is visible. Never gate a secret behind client logic; only the server can hold one.

### The real judgment: "server is truth" is not "validate everything"

Over-validating is a real overcorrection that burns server CPU and bandwidth for zero security benefit. The question a veteran asks is **"does a lie here have value to the cheater?"**

- **Adversarial → validate on the server**: currency, inventory, damage dealt, hit registration, item grants, anything an exploiter profits from. For hit-detection, rewind/lag-compensate server-side rather than trusting client-reported hits.
- **Non-adversarial → leave it client-authoritative**: camera shake, footstep particles, ragdoll death poses, which foot lands first, UI tween state. Round-tripping these through the server for "validation" adds latency and load for something nobody profits from faking.

### Network ownership (`:SetNetworkOwner`)

Physics simulation of an *unanchored* BasePart happens on whoever owns it. Roblox auto-assigns ownership based on player proximity and client hardware capacity — but for anything that matters you set it explicitly:

- `part:SetNetworkOwner(player)` → that client simulates locally (predict-and-correct), so **their own** vehicle/tool/character-attached physics can feel more responsive. The tradeoff is exploit surface: client-owned physics can be spoofed.
- `part:SetNetworkOwner(nil)` → force **server** ownership for anything contested or exploit-sensitive (projectiles that affect multiple players, physics that must be fair). The tradeoff is latency: server-owned physics feels laggy to the player pushing it.
- This lever — not RemoteEvents — is what makes vehicles and physics tools feel good. Its absence is the most common reason "my car lags for the driver."

## Remotes

| Primitive | Semantics | Use for |
|-----------|-----------|---------|
| **RemoteEvent** | Reliable, ordered, one-way | Most client↔server messages |
| **UnreliableRemoteEvent** | Unreliable, unordered | High-frequency, low-stakes (position updates, cosmetic effects) — saves bandwidth/latency |
| **RemoteFunction** | Request/response, yields | When you need a return value; **never `:InvokeClient()` from the server** (client can yield forever and hang the thread) |

Every `OnServerEvent` handler must:
1. **Rate-limit** per player (track last-call tick; reject within cooldown).
2. **Type-validate** every argument with `typeof()`.
3. **Bound values** (string length, numeric range, valid enum membership).
4. **Compute economy/stat changes on authoritative server state** — never trust a number the client sent.

Community typed-networking wrappers such as **Jolt** and **ByteNet** add strictly typed Luau APIs over these primitives. Check whether Roblox now ships an official typed networking API, and check each package's repo activity and releases, payload limits, and reliability semantics before adopting one.

### Anti-exploit patterns beyond validation

- **Dupe races**: two fires of an economy remote can land in the same frame before the first write commits, letting a player spend/receive twice. Process economy-affecting remotes through a **per-player serial queue** (or a single Heartbeat-driven state machine), not as independent handlers that assume they can't overlap. This is the exploit that survives naive per-call validation.
- **Speed/teleport hacks**: cap the believable `HumanoidRootPart` position delta per server Heartbeat and flag/reject implausible jumps — client-authoritative character movement means the server must sanity-check position, not just accept it.
- **Obfuscation is a speed bump, not a wall.** It slows a curious exploiter; it stops no one determined. Spend the effort on server checks, not on hiding client code.

## Data Persistence

| Layer | Tool | Status |
|-------|------|--------|
| Player data | **ProfileStore** | Community standard; successor to ProfileService (deprecated); check repo activity and releases before adopting |
| Key-value | **DataStoreService** | Built-in, GA |
| Cross-server ephemeral | **MemoryStoreService** | Built-in, GA |
| External/cloud | **Open Cloud DataStore APIs** | GA |

Non-negotiable durable rules:
- **One locking mechanism per piece of data, never two.** Use ProfileStore, which provides the atomic update and a session lease lock with expiry, so a crashed server's orphaned lock recovers. Hand-roll **`UpdateAsync`** (atomic read-then-write; never `SetAsync` on a shared key — two servers racing on `SetAsync` lose data) plus a leased lock keyed on `game.JobId` only when not using ProfileStore. Layering your own lock on top of ProfileStore adds writes against the shared budget and a second way for a stale lease to block a load.
- **Developer-product grants go through the profile.** Record each `PurchaseId` in the player's profile inside the single `MarketplaceService.ProcessReceipt` callback; return `PurchaseGranted` only after the grant and the `PurchaseId` are saved, and `NotProcessedYet` on any failure or when the player has left (see Known Traps in `../SKILL.md`).
- **`game:BindToClose(fn)`** to flush saves on shutdown (you get ~30s) — without it you lose the last autosave interval on every update/restart.
- Save on cadence (e.g. every 120s for progression) plus on critical events; never on every stat change (instant throttle).
- **DataStore has experience-level and server-level request limits.** Experience budgets are shared across servers and Open Cloud, separately by data-store/request type; `UpdateAsync` consumes read and write budgets. `GetRequestBudgetForRequestType()` reports the current server’s available requests. Look up current formulas, storage limits, and `SetRateLimitForRequestType()` configuration in the [official limits docs](https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits). Wrap calls in `pcall` and log failures.

### Production judgment the docs don't teach

- **When NOT to use ProfileStore.** Session-locking trades corruption-safety for load-time reliability. A player who crashes and rejoins before the lease expires hits a "load failed → kicked" loop — a real support-ticket generator at scale. Budget your lease/steal timing and show a **retry message**, not a silent kick. For low-consequence data (settings, cosmetic prefs), plain `UpdateAsync` without a session lock is often the right call — you avoid lock contention entirely and the corruption risk is trivial.
- **Budget bursts at both levels.** A server-local burst can hit its own limit; aggregate server/Open Cloud traffic can exhaust an experience request-type budget. Stagger initial loads, queue batch writes under the server’s available budget, and plan shared headroom from expected whole-experience concurrency. A server budget reading cannot prove experience-wide capacity remains.
- **Version your save schema.** Ship a `schemaVersion` field and a migration function that upcasts old profiles on load. ProfileStore reconciliation fills in *new* keys with template defaults automatically, but **renamed or restructured** keys need explicit migration — otherwise you silently lose or misread live players' progress on your next update.
- **MemoryStoreService** (sorted maps / queues, per-server-fast, TTL'd) is the right tool for cross-server ephemeral state — leaderboards-in-progress, matchmaking pools, rate counters — that would throttle DataStore.

## Architecture Patterns

- **CollectionService (tags)** — attach behavior to many instances via string tags with one manager script listening on `GetInstanceAddedSignal`/`GetInstanceRemovedSignal`. Far better than a `Script` per instance. Community wrapper **Stamp** turns tags into a reactive component system.
- **Connection discipline** — store every `RBXScriptConnection` and `:Disconnect()` it when its owner dies; or use a Maid/Janitor scoped to the player/character session. The per-respawn connect-without-disconnect leak is the most common silent memory leak.
- **Parallel Luau (`Actor`)** — the single Heartbeat thread is the bottleneck for CPU-bound per-entity work (large NPC AI ticks, procedural chunk generation, mass pathfinding). Move that work into an `Actor` and `task.desynchronize()` to run on a separate Luau VM thread in parallel; `task.synchronize()` before touching shared Instance state. Not for replication-sensitive logic, and synchronization has its own cost — profile before parallelizing small workloads. Pair with **`SharedTable`** to share large read-only data across Actors without copy cost.
- **Cross-server (`MessagingService`)** — successful games run dozens–thousands of server instances (each server has a player cap; look up the current maximum). Use `PublishAsync`/`SubscribeAsync` for global events, live-ops toggles, cross-server parties/matchmaking. Rate limits are aggressive and payloads cap at ~1 KB (`verify current numbers`); batch and throttle. It has **no delivery or ordering guarantee** — never use it as a payment/economy channel.
- **Large-project structure** — as a codebase grows past a few thousand lines, centralize shared services behind a small set of ModuleScripts, resolve dependencies in one direction (avoid circular `require()`s — they error or return partially-initialized tables), and unit-test pure Luau with **TestEZ**/**Jest-Roblox** run headless via **Lune** in CI.

## Module Frameworks

| Framework | Status (check repo activity and releases before adopting) | Recommendation |
|-----------|-------------------|----------------|
| Modular OOP (no framework) | Stable, common | Fine default for most worlds |
| **Matter** (`matter-ecs`) | Maintenance has been in doubt | Do not adopt for new production ECS without confirming recent activity on the canonical or fork repos |
| **Knit** | Declared unmaintained | Confirm repo status; do not start new projects on an unmaintained framework; legacy only |
| Flamework | UNVERIFIED status | Confirm maintenance before adopting |

## Skeleton Code

```lua
--!strict
-- ServerScriptService/PlayerData.server.luau — illustrative shape, not a drop-in
local Players = game:GetService("Players")
local ProfileStore = require(game.ServerScriptService.Packages.ProfileStore) -- via Wally

local TEMPLATE = { coins = 0 }
local store = ProfileStore.New("PlayerData", TEMPLATE)
local profiles: { [Player]: any } = {}

local function onAdded(player: Player)
    local profile = store:StartSessionAsync(`player_{player.UserId}`) -- session-locked
    if not profile then player:Kick("Data load failed") return end
    profiles[player] = profile
end

Players.PlayerAdded:Connect(onAdded)
Players.PlayerRemoving:Connect(function(player)
    local profile = profiles[player]
    if profile then profile:EndSession() end -- releases the lock + saves
    profiles[player] = nil
end)

game:BindToClose(function()
    for _, profile in profiles do profile:EndSession() end
end)
```

> Treat the API surface above as illustrative — verify ProfileStore's current method names against its docs, since community libraries rename across versions.

Sources: see [../data/sources.json](../data/sources.json) — task library, type checking, native codegen, UnreliableRemoteEvent, ProfileStore, CollectionService.
