# Performance & Known Traps

What kills Roblox experiences and how pros diagnose it. The *patterns* are durable; every numeric budget is volatile and labeled — most Roblox players are on mobile, so budgets are mobile-bound.

## Table of Contents

- [Geometry and Part Budgets](#geometry-and-part-budgets)
- [Static-Part Property Defaults](#static-part-property-defaults)
- [Draw Calls](#draw-calls)
- [Transparency and CSG Cost](#transparency-and-csg-cost)
- [Streaming for Performance](#streaming-for-performance)
- [Memory Leaks: the Connect Pattern](#memory-leaks-the-connect-pattern)
- [Client vs Server Work](#client-vs-server-work)
- [Profiling Workflow](#profiling-workflow)
- [Mobile and Low-End Constraints](#mobile-and-low-end-constraints)
- [Known Traps Catalog](#known-traps-catalog)

## Geometry and Part Budgets

Measure on the lowest target device; community figures for visible-part ceilings are starting heuristics, not limits, and mobile tolerates far fewer simultaneous visible parts than desktop. That mobile ceiling is the single most important world-scale constraint — find it with the MicroProfiler on a real low-end phone, not the emulator.
- Use StreamingEnabled to stay within limits on large maps without physically reducing geometry.
- For block-based worlds, greedy meshing to cut part count is the highest-leverage single optimization.

## Static-Part Property Defaults

For static environment geometry, set these (durable):

| Property | Set to | Why |
|----------|--------|-----|
| `Anchored` | `true` | Removes physics simulation overhead |
| `CanCollide` | `false` on non-traversable parts | Eliminates collision cost |
| `CastShadow` | `false` on decorative parts | Shadow rendering is costly |
| `Material` | `SmoothPlastic` | Cheapest; avoid Neon/ForceField on bulk geometry |
| `CollisionFidelity` | `Box` | `Precise` is expensive; `Box` is effectively free |
| `RenderFidelity` (MeshPart) | `Automatic` | `Precise` forces full-poly at all distances |
| `Transparency` | `0` by default; transparency where the effect needs it | Profile overlapping translucent surfaces |

## Draw Calls

Measure Scene Draw Count on the lowest target device and set your own budget there; published community targets are starting heuristics that drift with engine changes.

- Reuse identical mesh asset IDs and matching texture/SurfaceAppearance or material properties to enable instancing; measure the actual draw count rather than assuming MeshId + Material alone determines it.
- Particles can add draw calls and batch poorly; profile their cost and disable decorative emitters beyond a measured distance threshold.
- Read draw count in the F9 Developer Console / performance stats.

## Transparency and CSG Cost

- **Avoid heavy overlapping translucent geometry.** Overlapping partially transparent surfaces cause overdraw; retain transparency needed for the visual effect and profile it on target hardware. Prefer opaque geometry when transparency adds no value.
- CSG/Unions bake into a MeshPart at creation. The hidden cost is collision: union `CollisionFidelity` defaults to a precise convex hull that burns physics budget — set it to `Box` for unions that don't need precise player collision.

## Streaming for Performance

Covered mechanically in [world-building.md](world-building.md#streaming). Performance angle: streaming is how you serve a large world to a low-memory device. The trade is code complexity — LocalScripts must tolerate missing content and later stream-out. A bounded `WaitForChild(name, timeout)` can return `nil`; handle that result. Listen for removal, clean up bindings, and rebind on re-entry. Streaming parents objects to `nil` without calling `Destroy()`, so an initial successful wait does not establish lifetime availability.

## Memory Leaks: the Connect Pattern

The most common silent leak: connecting events per-character or per-respawn without disconnecting prior connections.

```lua
-- LEAK: a new Died connection every respawn, none cleaned up
player.CharacterAdded:Connect(function(character)
    character.Humanoid.Died:Connect(function() handleDeath() end)
end)
```

Fixes:
1. Store the `RBXScriptConnection` and `:Disconnect()` it when its owner dies.
2. Use `signal:Once(fn)` for single-fire events (auto-disconnects).
3. Use a **Maid/Janitor** scoped to the character/player session to batch-clean connections.

Rules of thumb: connections on `Humanoid`, `Touched`, `.Changed`, and `RunService.Heartbeat/Stepped` must be explicitly disconnected or scoped to their owner's lifetime. Connections auto-disconnect when the signal's Instance is `Destroy`ed — but only if you hold no external reference preventing garbage collection. Enable `Workspace.PlayerCharacterDestroyBehavior` to stop character-model memory accumulating across respawns.

## Client vs Server Work

- **Server:** authoritative state, persistence, economy transactions, cross-player physics, spawn/respawn.
- **Client:** visual tweens, animations, camera, local UI, particles, cosmetic CFrame updates.
- **Never run visual `TweenService` tweens on the server** — that replicates tween state to every client and wastes bandwidth. Tween locally; `FireAllClients()` to trigger.
- Measure incoming network per client on the lowest target device and budget it there; use `buffer` for dense custom replication; `Workspace:BulkMoveTo()` for batch CFrame updates instead of per-part assignment.

## Profiling Workflow

**MicroProfiler** (Ctrl+F6 in-game; server version via Developer Console):
- Pause at tall frame-peak bars; read which task label consumes the time (`render`, `physicsStep`, `heartbeat`, `updateUI`, or a user-script module name).
- Save `.html` dumps for async team analysis.

**F9 Developer Console → Memory tab:** find top-consuming asset categories (texture memory often unexpectedly exceeds the budget).

**Pro loop:** test at Graphics Quality ~10 on an older device → MicroProfiler for CPU/GPU peaks → Memory tab for the asset hog → fix → re-measure. Use the Network stats (not ping) to diagnose replication lag.

Set frame-time and memory targets from the lowest target device: frame time below your frame budget (about 16.7 ms at 60 FPS, 33.3 ms at 30 FPS) with headroom for peaks, and memory well below that device's ceiling. Look up Roblox's current published performance targets; treat any remembered MB figure as a starting heuristic.

## Mobile and Low-End Constraints

Most players are mobile — design to the ceiling, not the desktop.

- Reduce unique textures and image dimensions; texture memory alone can blow the mobile RAM ceiling.
- Store maps in `ServerStorage` (not `ReplicatedStorage`) until needed to keep client memory down.
- Disable `CastShadow` aggressively; prefer 9-slice images over `UICorner` on frequently-rendered UI.
- Offer a "Low Graphics" toggle that swaps to SmoothPlastic and disables decorative emitters.
- `Workspace.PhysicsSteppingMethod = "Adaptive"` and `ClientAnimatorThrottling = true` meaningfully cut mobile CPU (`verify property names`).

## Known Traps Catalog

| Trap | Symptom | Fix |
|------|---------|-----|
| `wait()` drift | Timing slips under load | `task.wait` |
| Busy-wait loop | Threads never terminate; CPU waste | Event-driven (`.Changed`, `GetPropertyChangedSignal`) |
| Client-side state change | Server/others don't see it | Ordinary local edits do not update server state; request validated server mutations. Client-owned physics can replicate and needs separate validation |
| Unvalidated `OnServerEvent` | Exploiter sends arbitrary args | Rate-limit + `typeof()` + bounds + compute on server state |
| `RemoteFunction:InvokeClient()` from server | Server thread hangs forever | Never call it; use RemoteEvent both ways |
| `SetAsync` on shared key | Data loss on concurrent save | `UpdateAsync` (atomic) |
| No `BindToClose` | Lose last autosave on shutdown | `game:BindToClose` to flush saves |
| No session lock | Duplication/overwrite on fast rejoin/teleport | ProfileStore's lease lock, or a hand-rolled `game.JobId` lease with expiry when not using ProfileStore — never both |
| Non-idempotent `ProcessReceipt` | Dev-product purchases granted twice, or charged and never granted | One dispatcher per server; persist grant + `PurchaseId` together for cross-server deduplication; `PurchaseGranted` only after the save, `NotProcessedYet` on failure or absent player |
| Paid random item with no policy check | Sold where paid random items are restricted | Server-side `PolicyService:GetPolicyInfoForPlayerAsync` gate per player; disclose odds per current policy (look up) |
| DataStore throttle | Writes silently queue/drop | Save on cadence + events, `pcall` + log, fewer writes; check both server/request-type and shared experience limits; the budget API reports the current server’s availability — see luau-and-architecture.md |
| Direct Workspace index in LocalScript | Intermittent nil errors (replication/stream timing) | Bounded wait + handle `nil`; clean up on removal and rebind on stream-in |
| Humanoid race on `CharacterAdded` | `Humanoid`/`HumanoidRootPart` nil on first/fast spawn | `character:WaitForChild("Humanoid")` |
| `Instance.new("Part", parent)` | Extra replication events as you set properties | Set properties first, `.Parent` last |
| Partial transparency on bulk geometry | Overlapping surfaces cause overdraw | Prefer opaque when possible; profile necessary transparency |
| Per-instance Scripts | Unmaintainable, harder to profile | CollectionService tag + one manager |
| Connect without Disconnect | Growing memory over a session | Disconnect / `Once` / Maid |
| Emulator-only testing | Ships fine in Studio, lags on phones | Test on a real low-end Android |
| Unrated experience | Unplayable or hidden for users, depending on the current rule (look it up) | Complete the maturity questionnaire (see discovery reference) |

Sources: see [../data/sources.json](../data/sources.json) — performance considerations thread, optimization guide (memory/draw/network), Connect-leak thread, session-locking thread, MicroProfiler docs, securing-remotes thread.
