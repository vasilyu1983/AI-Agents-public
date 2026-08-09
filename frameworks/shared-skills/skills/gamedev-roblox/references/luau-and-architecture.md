# Luau & Architecture (Jul 2026)

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

Luau is statically-typed, gradually-typed Lua. The 2026 baseline:

- Write new code with type annotations and a strictness mode declared at the top of the file.
- Prefer the `task` library, `vector` built-in, and `buffer` for binary data.
- The **New Type Solver** went GA November 2025. `--!nonstrict`/`--!nocheck` files were migrated automatically; `--!strict` files remain on the old solver by default through 2026 unless you opt in via the `UseNewLuauTypeSolver` workspace property (`as of May 2026 — verify the migration timeline`).

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
- Platform note: native codegen for the **Android client** was still a roadmap item (`as of May 2026 — verify`); do not assume mobile native speedups.
- `buffer` is a built-in type for compact binary data (with `buffer.readbits`/`writebits`). Pairs with native codegen and is the tool for dense custom replication payloads.

## Client-Server Model

Server-authoritative, always. FilteringEnabled is permanently on and cannot be disabled.

| Context | Runs where | Trust |
|---------|-----------|-------|
| `Script` | Server | Trusted |
| `LocalScript` | Client | **Untrusted** — exploitable |
| `ModuleScript` | In the context of its requirer | Inherits caller's trust |

Implications:
- A property or instance change made in a LocalScript is client-side only — the server and other players do not see it. Beginners change currency/health locally and wonder why it doesn't persist; it never will.
- Cheaters can run LocalScript-equivalent code via executors. The server must validate everything that affects shared state.
- **Client code is fully readable.** Exploiters decompile LocalScript bytecode trivially — every constant you ship (drop rates, prices, `--!strict` types, "secret" thresholds) is visible. Never gate a secret behind client logic; only the server can hold one.

### The real judgment: "server is truth" is not "validate everything"

Over-validating is a real overcorrection that burns server CPU and bandwidth for zero security benefit. The question a veteran asks is **"does a lie here have value to the cheater?"**

- **Adversarial → validate on the server**: currency, inventory, damage dealt, hit registration, item grants, anything an exploiter profits from. For hit-detection, rewind/lag-compensate server-side rather than trusting client-reported hits.
- **Non-adversarial → leave it client-authoritative**: camera shake, footstep particles, ragdoll death poses, which foot lands first, UI tween state. Round-tripping these through the server for "validation" adds latency and load for something nobody profits from faking.

### Network ownership (`:SetNetworkOwner`)

Physics simulation of an *unanchored* BasePart happens on whoever owns it. Roblox auto-assigns ownership of loose parts to the nearest player for responsiveness — but for anything that matters you set it explicitly:

- `part:SetNetworkOwner(player)` → that client simulates locally (predict-and-correct), so **their own** vehicle/tool/character-attached physics feels lag-free. The tradeoff is exploit surface: client-owned physics can be spoofed.
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

Community typed-networking wrappers such as **Jolt** and **ByteNet** add strictly typed Luau APIs over these primitives. No official typed networking API exists yet; verify package activity, payload limits, and reliability semantics before adopting one.

### Anti-exploit patterns beyond validation

- **Dupe races**: two fires of an economy remote can land in the same frame before the first write commits, letting a player spend/receive twice. Process economy-affecting remotes through a **per-player serial queue** (or a single Heartbeat-driven state machine), not as independent handlers that assume they can't overlap. This is the exploit that survives naive per-call validation.
- **Speed/teleport hacks**: cap the believable `HumanoidRootPart` position delta per server Heartbeat and flag/reject implausible jumps — client-authoritative character movement means the server must sanity-check position, not just accept it.
- **Obfuscation is a speed bump, not a wall.** It slows a curious exploiter; it stops no one determined. Spend the effort on server checks, not on hiding client code.

## Data Persistence

| Layer | Tool | Status |
|-------|------|--------|
| Player data | **ProfileStore** | Community standard; successor to ProfileService (deprecated) |
| Key-value | **DataStoreService** | Built-in, GA |
| Cross-server ephemeral | **MemoryStoreService** | Built-in, GA |
| External/cloud | **Open Cloud DataStore APIs** | GA |

Non-negotiable durable rules:
- Use **`UpdateAsync`** (atomic read-then-write), never `SetAsync` on a shared key — two servers racing on `SetAsync` lose data.
- **Session-lock** data keyed on `game.JobId` with a lease expiry, so a crashed server's orphaned lock recovers. ProfileStore does this for you.
- **`game:BindToClose(fn)`** to flush saves on shutdown (you get ~30s) — without it you lose the last autosave interval on every update/restart.
- Save on cadence (e.g. every 120s for progression) plus on critical events; never on every stat change (instant throttle).
- **DataStore budget changed shape in early 2026 — this is a confirmed break from the old mental model, not a minor tweak.** Request access and storage moved from **per-server** to **per-experience**: every running server instance of your experience now draws from **one shared request-budget pool and one shared storage cap**, not an independent budget each (legacy per-server formula was roughly `60 + numPlayers*10` requests/min, *per server*). Roblox ships a Data Stores Manager, storage notifications, and a batch processor to help manage this; **Extended Services** lets you purchase capacity beyond the platform limit if you outgrow it. Wrap every call in `pcall` and log failures regardless. (Source: DevForum "DataStores Access and Storage Updates," 2026 — verify current numeric caps before quoting.)

### Production judgment the docs don't teach

- **When NOT to use ProfileStore.** Session-locking trades corruption-safety for load-time reliability. A player who crashes and rejoins before the lease expires hits a "load failed → kicked" loop — a real support-ticket generator at scale. Budget your lease/steal timing and show a **retry message**, not a silent kick. For low-consequence data (settings, cosmetic prefs), plain `UpdateAsync` without a session lock is often the right call — you avoid lock contention entirely and the corruption risk is trivial.
- **DataStore budget is now a per-*experience* pool, not per-server, not per-player** (corrected 2026 model, see above). This makes the failure mode *worse*, not better, at scale: a burst on **any one** server of your experience — 30 players joining a fresh server in 10s, or a "reward everyone online" loop firing on several servers near-simultaneously — can exhaust the write budget for **every server of the experience at once**, not just the one that caused it. Stagger initial loads with `task.wait` jitter; never loop `UpdateAsync` synchronously over all online players; check `DataStoreService:GetRequestBudgetForRequestType()` before a batch op and drain a queue under budget; for a large concurrent-user game, budget headroom against your *whole player base*, not per-server CCU.
- **Version your save schema.** Ship a `schemaVersion` field and a migration function that upcasts old profiles on load. ProfileStore reconciliation fills in *new* keys with template defaults automatically, but **renamed or restructured** keys need explicit migration — otherwise you silently lose or misread live players' progress on your next update.
- **MemoryStoreService** (sorted maps / queues, per-server-fast, TTL'd) is the right tool for cross-server ephemeral state — leaderboards-in-progress, matchmaking pools, rate counters — that would throttle DataStore.

## Architecture Patterns

- **CollectionService (tags)** — attach behavior to many instances via string tags with one manager script listening on `GetInstanceAddedSignal`/`GetInstanceRemovedSignal`. Far better than a `Script` per instance. Community wrapper **Stamp** turns tags into a reactive component system.
- **Connection discipline** — store every `RBXScriptConnection` and `:Disconnect()` it when its owner dies; or use a Maid/Janitor scoped to the player/character session. The per-respawn connect-without-disconnect leak is the most common silent memory leak.
- **Parallel Luau (`Actor`)** — the single Heartbeat thread is the bottleneck for CPU-bound per-entity work (large NPC AI ticks, procedural chunk generation, mass pathfinding). Move that work into an `Actor` and `task.desynchronize()` to run on a separate Luau VM thread in parallel; `task.synchronize()` before touching shared Instance state. Not for replication-sensitive logic, and synchronization has its own cost — profile before parallelizing small workloads. Pair with **`SharedTable`** to share large read-only data across Actors without copy cost.
- **Cross-server (`MessagingService`)** — successful games run dozens–thousands of server instances (a server caps at ~700 players). Use `PublishAsync`/`SubscribeAsync` for global events, live-ops toggles, cross-server parties/matchmaking. Rate limits are aggressive and payloads cap at ~1 KB (`verify current numbers`); batch and throttle. It has **no delivery or ordering guarantee** — never use it as a payment/economy channel.
- **Large-project structure** — as a codebase grows past a few thousand lines, centralize shared services behind a small set of ModuleScripts, resolve dependencies in one direction (avoid circular `require()`s — they error or return partially-initialized tables), and unit-test pure Luau with **TestEZ**/**Jest-Roblox** run headless via **Lune** in CI.

## Module Frameworks

| Framework | Status (May 2026) | Recommendation |
|-----------|-------------------|----------------|
| Modular OOP (no framework) | Stable, common | Fine default for most worlds |
| **Matter** (`matter-ecs`) | **Dormant** — no confirmed 2026 activity | Do not adopt for new production ECS without independently confirming maintenance |
| **Knit** | **No longer maintained** | Do not start new projects on it; legacy only |
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
