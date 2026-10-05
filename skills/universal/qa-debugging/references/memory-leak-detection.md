# Memory Leak Detection

How to tell a leak from normal memory growth, find what keeps the memory alive, and prove the
fix. Common leak shapes (unremoved listeners, unbounded caches, missing effect cleanup,
un-cancelled goroutines) are assumed knowledge.

## Contents

- [First: Is It a Leak?](#first-is-it-a-leak)
- [Which Number to Watch](#which-number-to-watch)
- [Find the Retainer](#find-the-retainer)
- [Runtime Notes](#runtime-notes)
- [Containers and OOM](#containers-and-oom)
- [Proving the Fix](#proving-the-fix)

---

## First: Is It a Leak?

Rule out these before calling it a leak:

| Pattern | Looks like | Actually is | Check |
|---------|-----------|-------------|-------|
| Rises then plateaus | Leak on a short graph | Warm-up: caches, JIT, pools, lazy init | Watch past the plateau under steady load |
| Heap flat, RSS grows | Leak | Allocator fragmentation or native/off-heap memory (buffers, C extensions, thread stacks) | Compare heap metric vs RSS; see below |
| RSS stays high after load drops | Leak | Runtime or allocator holding freed memory without returning it to the OS | Force GC; check whether RSS stays level on the next load cycle rather than climbing |
| Grows with traffic, falls with it | Leak | Load-proportional working set | Normalize by concurrent requests |
| Python reference cycles | Leak | Delayed collection: the cycle collector frees unreachable cycles | Real leak only if still reachable from a global/registry, or `gc.disable()` is in use |

**A leak is sustained growth under steady load after warm-up, surviving a forced GC.**
Anything else needs a different fix (limits, tuning, capacity), not a leak hunt.

## Which Number to Watch

- **RSS** is what the OS and the OOM killer care about. **Heap used** is what the GC manages. If
  only RSS grows, profile native allocations; a heap snapshot will show nothing.
- **VMS (virtual size) is not heap and not memory use.** Runtimes reserve large virtual ranges
  they never touch. Never alert on VMS or label it as heap.
- Distinguish kubelet eviction from a cgroup OOM kill. Kubelet node-pressure eviction estimates
  available memory excluding inactive file cache; the kernel's cgroup limit accounts charged
  memory and invokes OOM if reclaim cannot bring it below the hard limit. Check `memory.events`,
  the pod termination reason, and the dashboard's metric before attributing a kill to RSS or
  working set ([kernel](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html),
  [kubelet](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)).
- **Alert on time-to-limit, not a fixed MB/hour.** A slope that is harmless at a 16 GB limit is
  an outage at 512 MB. Compute headroom divided by sustained slope and alert when it falls below
  your restart or deploy interval. There is no universal threshold; set it from your own baseline.
- Glibc malloc fragmentation in multithreaded services (many arenas) is a common "leak" that is
  not one. Swapping the allocator (jemalloc, mimalloc) or capping arenas (`MALLOC_ARENA_MAX`) is a
  test of that hypothesis: if RSS growth stops, the cause was fragmentation.

## Find the Retainer

An allocation profiler answers "who allocated this?" A heap snapshot answers "who is keeping it
alive?" The fix goes at the **retainer**, so prefer the retainer view.

**Three-snapshot technique (any heap-snapshot runtime):**

1. Warm up, force GC, snapshot A.
2. Repeat the suspect action N times, force GC, snapshot B.
3. Repeat N more times, force GC, snapshot C.
4. Leaked objects are those whose count grows by about N in both A→B and B→C. Objects that grew
   only once are caches or warm-up. Follow their retainer paths to the first object your code
   owns: that is the leak site.

**Snapshot cost warning:** a heap snapshot pauses the process and can need memory on the order
of the heap itself. On a container near its limit, taking a snapshot can trigger the OOM kill
you are investigating. Take it on a drained instance, or raise the limit on one replica first.
Snapshots contain user data; handle them as production data.

## Runtime Notes

| Runtime | Default tool | Non-obvious point |
|---------|--------------|-------------------|
| Node.js | Heap snapshots via DevTools (`node --inspect`, or `kill -USR1 <PID>` to open the inspector on a running process); `--heapsnapshot-near-heap-limit=N` to capture automatically before OOM | `v8.writeHeapSnapshot()` is synchronous and blocks the event loop; `external`/`arrayBuffers` growth is off-heap (Buffers) and invisible in the JS heap view |
| Browser | DevTools Memory: snapshot comparison, filter "Detached" | Detached DOM kept alive by a listener or closure is the usual SPA leak; repeat open/close N times, not once |
| Python | `tracemalloc` snapshot `compare_to` for Python objects; `memray` for native allocations and running processes | tracemalloc misses C-extension allocations; if RSS grows but tracemalloc is flat, use memray |
| JVM | `jcmd <PID> GC.heap_dump`, analyze dominator tree (Eclipse MAT) | Heap flat but RSS growing: enable Native Memory Tracking (`-XX:NativeMemoryTracking=summary`) for Metaspace, direct buffers, thread stacks; classloader leaks show as Metaspace growth after redeploys |
| Go | `pprof` heap (`inuse_space`) and goroutine profiles | Goroutine count growth is the most common Go leak; the Go runtime returns memory to the OS lazily, so RSS lags heap drops; `GOMEMLIMIT` sets a soft limit |
| C / C++ | ASan/LeakSanitizer in tests; heaptrack or a BPF allocation profiler for long-running growth | Valgrind "still reachable" at exit is usually not a leak; "definitely lost" is |
| Rust | Heap profiler (heaptrack, dhat) | Leaks come from `Rc`/`Arc` cycles, `mem::forget`, or unbounded collections, not missing frees |

## Containers and OOM

- Set the runtime's heap ceiling below the container limit, leaving room for off-heap, native,
  and thread-stack memory (Node `--max-old-space-size`, JVM `-XX:MaxRAMPercentage`, Go
  `GOMEMLIMIT`). A heap limit equal to the container limit guarantees kernel OOM kills instead of
  catchable runtime errors.
- Exit code 137 means SIGKILL, not necessarily OOM. Confirm with the pod's last-state reason
  (`OOMKilled`) or the kernel log before treating it as memory.
- Capture before restart: if the process is still alive and growing, take the snapshot or heap
  dump first (see the cost warning above). An automatic restart policy destroys the evidence;
  capture on the way down (`--heapsnapshot-near-heap-limit`, JVM `-XX:+HeapDumpOnOutOfMemoryError`
  to a writable volume).

## Proving the Fix

- Re-run the three-snapshot test: the leaked type's count must stay flat across both deltas.
- Run a soak at steady load for longer than the time it took to reach the original failure,
  and compare the post-warm-up slope before and after.
- A scheduled restart or a larger limit is mitigation, not a fix. Record it as such, with the
  measured slope, so it is not mistaken for closure.
