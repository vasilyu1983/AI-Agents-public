# Systems Debugging Tools

Which low-level tool earns the investigation, and the traps that make each one lie or hurt.
Command syntax for strace, lsof, perf, gdb, lldb, and dtrace is assumed knowledge; check
`man` or `--help` on the target host because flags differ by distro and version.

## Contents

- [Tool Selection](#tool-selection)
- [Tracing and Profiling Traps](#tracing-and-profiling-traps)
- [rr: Capture Once, Replay Forever](#rr-capture-once-replay-forever)
- [Live-Process Attach and Flight Recorders](#live-process-attach-and-flight-recorders)
- [Core-Dump Workflow](#core-dump-workflow)

---

## Tool Selection

| Symptom | Default first tool | Switch when |
|---------|--------------------|-------------|
| Silent failure, no logs | `strace -f -e trace=file,network -p <PID>` (look for `ENOENT`, `EACCES`, `EPERM`) | Production host under load: use `perf trace` or a bpftrace one-liner instead (see traps) |
| Port conflict, FD exhaustion | `lsof -p <PID>` / `lsof -i :<port>`; count `/proc/<PID>/fd` | FD count grows over time: treat as a leak, see `memory-leak-detection.md` |
| CPU hotspot (Linux) | `perf record -F 99 -g -p <PID> -- sleep 30`, then a flame graph | Need always-on history: continuous profiler (owned by `../../qa-observability/SKILL.md`) |
| Syscall latency, argument sniffing in production | bpftrace one-liner or BCC tools (`execsnoop`, `opensnoop`, `biolatency`) | Kernel too old for BPF or no root: fall back to `strace` on a canary |
| Service you cannot recompile, need HTTP/gRPC/DB spans | eBPF auto-instrumentation (OpenTelemetry eBPF Instrumentation, Grafana Beyla, Pixie) | Need business attributes on spans: SDK instrumentation instead |
| Native crash, process gone | Core dump + `gdb`/`lldb` (see workflow below) | No core captured: enable capture first, then wait for recurrence |
| Heisenbug, flaky native test, race | `rr record`, replay offline | Hardware counters unavailable: rr.soft; team needs shared session: Pernosco |
| macOS syscall / Obj-C tracing | `fs_usage`, `sample <PID>`, Instruments | Needs scriptable probes: check whether `dtrace` can inspect the target under the host's SIP and process restrictions |
| Hung process you cannot restart | Attach tools below (py-spy, jstack/jcmd, `gdb -p` + `thread apply all bt`) | Must see the seconds before the event: flight recorder |

eBPF auto-instrumentation tools differ in env-var namespace and language coverage between the
upstream OpenTelemetry project and vendor distributions; they are not drop-in compatible. Read
the project's current configuration and support-matrix docs before depending on one.

## Tracing and Profiling Traps

- **strace is ptrace-based and can slow a syscall-heavy process by an order of magnitude or
  more.** On a production host that is a self-inflicted incident. Prefer `perf trace` or BPF,
  which do not stop the process on every syscall; keep `strace` for local repro or a drained
  canary.
- **Observer effect on timing bugs.** strace, gdb breakpoints, and verbose logging all change
  scheduling. A race that vanishes under them is evidence of timing dependence, not a fix.
  Switch to capture-once (rr) instead of adding more observation.
- **perf stacks are only as good as the unwinder.** Binaries built without frame pointers give
  truncated or wrong stacks with plain `-g`; use `--call-graph dwarf` (larger data) or rebuild
  with frame pointers. JIT runtimes need a perf map (JVM `-XX:+PreserveFramePointer` plus a
  perf-map agent, Node `--perf-basic-prof`) or frames show as hex.
- **Sample at an odd rate** (`-F 99`, not 100) so sampling does not run in lockstep with
  periodic timers and over-count them.
- **Containers hide symbols and PIDs.** Profile from the host with the container's PID
  namespace mapped, or run the profiler inside the container with the binary's debug symbols
  reachable (debuginfod, below).
- **Off-CPU time is invisible to on-CPU profilers.** A service slow because it waits on locks,
  I/O, or the network shows a cold CPU flame graph. Use an off-CPU profile (BCC `offcputime`) or
  a wall-clock profiler before concluding "not CPU, so not our code."

## rr: Capture Once, Replay Forever

**Use rr when** a native (C, C++, Rust, Go with caveats) failure is timing-dependent or
CI-only: re-running resamples the scheduler and yields no new information, while one rr
recording of the failing run can be replayed deterministically as many times as needed,
including backwards.

```bash
rr record ./my-test --filter=flaky_case     # record until the failure is captured
rr record --chaos ./my-test                 # chaos mode: randomizes scheduling to surface rare interleavings
rr replay                                   # gdb session on the recorded execution
(gdb) watch -l obj->field                   # then:
(gdb) reverse-continue                      # jump back to the last write that corrupted it
```

The high-value move is the reverse watchpoint: find the corrupted value at the crash, set a
watchpoint on it, and reverse-continue to the exact write. That replaces hours of hypothesis
logging.

**When not to use rr:**

- **rr runs all threads of the recorded process on a single core.** A parallel workload slows
  roughly in proportion to how much it relied on parallelism, and a race that needs true
  simultaneous execution on two cores may never appear. Use `--chaos`, or fall back to TSan with
  adaptive delay (`race-condition-diagnosis.md`) when the bug depends on real parallelism.
- Not for production: recording cost is too high. Record in CI or staging.
- Recording needs Linux and CPU hardware performance counters. Most cloud VMs and Linux VMs on
  Apple Silicon do not expose them. The fallback is **rr.soft**, an experimental fork that is not
  merged upstream: record with `rr record -W`, and replay also needs `-W`. Prefer upstream rr on
  hardware that supports it.
- Some workloads using unusual kernel interfaces or GPU/driver features cannot be recorded; if a
  recording fails, check the rr FAQ before investing more.

Check the rr release notes and `rr --version` on the recording host for current kernel,
`perf_event_paranoid`, and debugger-integration requirements; these change between releases.

**CI pattern:** run the flaky suite under `rr record`, upload the trace directory as an
artifact only on failure, replay locally. This removes "cannot reproduce" as a blocker.

**Pernosco** (hosted omniscient debugger over rr recordings) is worth adding when replay
navigation itself becomes the bottleneck (long multi-threaded runs), or when several engineers
must share and annotate one failing execution. A single engineer with a short recording does not
need it.

## Live-Process Attach and Flight Recorders

For a running process you cannot restart, attach before you redeploy with more logging. A
restart destroys the evidence.

- **Python, default: `py-spy dump --pid <PID>`.** No code change, works on a process you do not
  control, prints all-thread stacks.
- **Python 3.14+: `python -m pdb -p <PID>`** attaches a live debugger without a pre-placed
  breakpoint (PEP 768). Confirm availability for the exact Python build first.
- **Python, pre-arranged: `faulthandler.register(signal.SIGUSR1, all_threads=True)`** at
  startup, then `kill -USR1 <PID>` dumps stacks and the process survives. `faulthandler.enable()`
  alone only covers fatal signals; sending SIGUSR1 to a process without the registered handler
  runs the default action and **kills the process you were trying to inspect**.
- **JVM:** `jcmd <PID> Thread.print` (or `jstack`) for stacks; keep Java Flight Recorder in
  continuous ring-buffer mode and dump it on anomaly.
- **Go 1.25+:** `runtime/trace.FlightRecorder` keeps the last seconds of execution trace in
  memory and writes it on demand, so you get the window before the bad event without always-on
  tracing cost. Check the `runtime/trace` docs for your Go version. For goroutine stacks now:
  `SIGQUIT` dumps them but exits the process; prefer the `net/http/pprof` goroutine endpoint.
- **Native:** `gdb -p <PID> -batch -ex 'thread apply all bt'` then detach; `gcore <PID>` writes a
  core without killing the process, so analysis can continue after mitigation.

## Core-Dump Workflow

For a crash that already happened, the core dump is the evidence. Capture it before restarting
or redeploying anything.

```bash
coredumpctl list                      # systemd hosts: index of captured cores
coredumpctl debug <PID-or-exe>        # opens gdb on the matching core
gdb -batch -ex 'bt full' -ex 'thread apply all bt' ./my-binary core.1234   # non-interactive, for CI
export DEBUGINFOD_URLS="https://debuginfod.example.com"   # fetch symbols for stripped prod binaries
```

- **Keep symbols out of the image but reachable.** Ship stripped binaries and publish debug info
  to a debuginfod or symbol server keyed by build ID. A core without matching symbols is nearly
  useless, and a rebuilt binary does not match.
- **Containers suppress cores by default** (`ulimit -c 0`, read-only filesystem, `core_pattern`
  owned by the host). Configure a writable crash directory or host-side capture, and test it
  before an incident, not during one.
- **Cores can contain secrets and PII** (request bodies, tokens in memory). Store them with the
  same access controls as production data and set a retention limit.
