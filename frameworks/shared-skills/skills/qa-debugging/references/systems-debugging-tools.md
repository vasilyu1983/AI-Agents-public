# Systems Debugging Tools

Quick reference for low-level and systems debugging tools. Each entry covers when to reach for it and one or two example commands.

---

## Contents

- [strace / ltrace](#strace--ltrace)
- [lsof](#lsof)
- [perf](#perf)
- [eBPF Tools](#ebpf-tools)
- [lldb (Swift / C / C++ / Rust)](#lldb-swift--c--c--rust)
- [gdb Basics](#gdb-basics)
- [dtrace (macOS)](#dtrace-macos)
- [rr — Deterministic Record and Replay](#rr--deterministic-record-and-replay)
- [Pernosco — Omniscient Debugging on top of rr](#pernosco--omniscient-debugging-on-top-of-rr)

---

## strace / ltrace

**When to reach for it**: You need to see every system call (strace) or library call (ltrace) a process is making — file opens, socket connects, ioctl failures, unexpected `EPERM` or `ENOENT` errors. Useful when logs are silent but the process behaves wrongly.

```bash
# Trace all syscalls for a running PID; filter to file-related ones
strace -f -e trace=file -p <PID>

# Trace a new process and save the full log for post-analysis
strace -o /tmp/trace.txt -tt -f ./my-binary --arg
```

```bash
# Trace library calls (ltrace) to find unexpected malloc/free or third-party calls
ltrace -e malloc+free -p <PID>
```

**Note**: strace adds significant overhead. Use sparingly in production; prefer a test environment when possible.

---

## lsof

**When to reach for it**: Diagnosing file descriptor leaks, finding which process owns a port, checking open sockets, or confirming that a library or data file is actually loaded.

```bash
# Show all open files for a specific PID
lsof -p <PID>

# Find which process is listening on port 8080
lsof -i :8080
```

```bash
# Check for file descriptor exhaustion (count open FDs per process)
lsof -u <username> | wc -l
```

---

## perf

**When to reach for it**: CPU profiling, finding hot functions, diagnosing kernel vs userspace time splits, cache misses, branch mispredictions, or I/O wait. The go-to Linux performance tool before reaching for heavier profilers.

### perf top

Live, top-like view of CPU hotspots across the whole system:

```bash
# Live per-symbol CPU breakdown (requires kernel symbols for kernel frames)
perf top -g --call-graph dwarf
```

### perf record / report

Capture a profile to disk, then analyze offline — safe for short production bursts:

```bash
# Record for 30 seconds on a specific PID, with call graphs
perf record -F 99 -g -p <PID> -- sleep 30

# Generate flamegraph-compatible report in the terminal
perf report --stdio --call-graph=graph
```

**Tip**: Use `perf script | flamegraph.pl` (Brendan Gregg's tools) to generate a flame graph SVG.

---

## eBPF Tools

eBPF lets you attach small verified programs to kernel hooks at runtime — zero recompilation, near-zero overhead at rest.

### bpftrace One-Liners

**When to reach for it**: Ad-hoc tracing with a one-liner — syscall latency histograms, argument sniffing, return-value inspection — without writing a full BCC program.

```bash
# Histogram of read() latency in microseconds across all processes
bpftrace -e 'kretprobe:vfs_read { @us = hist((nsecs - @start[tid]) / 1000); } kprobe:vfs_read { @start[tid] = nsecs; }'

# Trace all execve calls with arguments (useful for debugging spawned subprocesses)
bpftrace -e 'tracepoint:syscalls:sys_enter_execve { printf("%s %s\n", comm, str(args->filename)); }'
```

### BCC Collection

**When to reach for it**: Production-safe, purpose-built tools for common scenarios. Ships with named scripts (`execsnoop`, `opensnoop`, `tcpconnect`, `biolatency`, etc.).

```bash
# Watch all new processes spawned system-wide (great for debugging daemons or CI runners)
/usr/share/bcc/tools/execsnoop

# Trace open() calls and show which files are being accessed and by whom
/usr/share/bcc/tools/opensnoop -p <PID>
```

### Pixie / Beyla / OTel eBPF Instrumentation (OBI) — Auto-Instrumentation

**When to reach for it**: Kubernetes or containerised services where adding an agent or recompiling is not feasible. These tools inject eBPF probes to capture HTTP, gRPC, database, and DNS traffic automatically.

- **Pixie**: deploy to a Kubernetes cluster; query with PxL scripts from the CLI or UI. No code changes required.
- **Beyla** (Grafana): attaches to a running binary via `BEYLA_OPEN_PORT` or process name; exports OpenTelemetry traces to your existing collector. In 2025, Grafana donated Beyla's core instrumentation engine to the OpenTelemetry project as **OTel eBPF Instrumentation (OBI)**, making it a first-class OTel component.
- **OBI** (`opentelemetry-ebpf-instrumentation`): the upstream OTel project form of Beyla's engine; supports Go, Python, Node.js, Java, and Rust via uprobes; emits standard OTLP spans.

```bash
# Beyla / OBI: auto-instrument a process by port and export OTLP spans
BEYLA_OPEN_PORT=8080 OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 beyla
```

---

## lldb (Swift / C / C++ / Rust)

**When to reach for it**: Native crash analysis, setting breakpoints in Swift/Obj-C/C++/Rust code, inspecting memory, or post-mortem analysis of a `.crash` file or core dump on Apple platforms (and Linux).

```bash
# Attach to a running process
lldb -p <PID>

# Load a binary and set a breakpoint before running
lldb ./my-binary
(lldb) breakpoint set --name main
(lldb) run --arg1 value
```

```bash
# Post-mortem: load a core dump
lldb ./my-binary -c core.dump
(lldb) bt          # print backtrace
(lldb) frame var   # inspect local variables in current frame
```

**Swift-specific**: use `expr` to call Swift expressions inline:

```
(lldb) expr import Foundation
(lldb) expr let x = myObject.someProperty; print(x)
```

---

## gdb Basics

**When to reach for it**: C/C++ and Rust debugging on Linux where lldb is unavailable or when the toolchain defaults to gdb (GCC, most Linux distros).

```bash
# Start debugging a binary with arguments
gdb --args ./my-binary --flag value

# Core dump post-mortem
gdb ./my-binary core
(gdb) bt full      # full backtrace with locals
(gdb) info locals  # local variables in current frame
```

```bash
# Attach to a running process and catch the next segfault
gdb -p <PID>
(gdb) catch signal SIGSEGV
(gdb) continue
```

**Useful gdb one-liners**:

```bash
# Non-interactive: print backtrace and quit (CI crash reports)
gdb -batch -ex "bt" -ex "quit" ./my-binary core
```

---

## dtrace (macOS)

**When to reach for it**: macOS kernel and user-space probing without rebooting. Useful for syscall latency, I/O tracing, Objective-C method tracing, and process activity monitoring when Instruments is too heavy or you need scriptable output.

> Requires SIP partially disabled for kernel probes, or use only pid/process-level probes in standard mode.

```bash
# Count syscalls by name for a specific PID over 10 seconds
sudo dtrace -n 'syscall:::entry /pid == $1/ { @[probefunc] = count(); }' -p <PID> -c "sleep 10"

# Trace all Objective-C method calls in an app by name (great for finding unexpected callsites)
sudo dtrace -n 'objc$target:NSURLSession:-*:entry { printf("%s\n", probefunc); }' -p <PID>
```

```bash
# File I/O latency histogram for a process (nanoseconds)
sudo dtrace -n '
  io:::start /pid == $1/ { self->ts = timestamp; }
  io:::done  /self->ts/  { @lat = quantize(timestamp - self->ts); self->ts = 0; }
' -p <PID>
```

**macOS alternative**: For lighter work, `fs_usage` and `vm_stat` often suffice and require no SIP changes:

```bash
sudo fs_usage -w -f filesys <PID>   # file-system calls with timing
```

---

## rr — Deterministic Record and Replay

**When to reach for it**: Heisenbugs (failures that disappear under a debugger), flaky CI failures that cannot be reproduced on demand, race conditions, and any failure mode where re-running is not reliable. rr records all kernel inputs and nondeterministic CPU effects so the replay is bit-for-bit identical to the original execution. You can then reverse-execute the replay as many times as needed with gdb or lldb.

**Platform**: Linux only for the recording host (kernel ≥ 4.7). Requires Intel Nehalem (2010) or later, AMD Zen or later, or AArch64 chips where support is now production-quality (AWS Graviton, Cortex/Neoverse, Apple M1+ when running Linux on bare metal). macOS cannot record natively — use **rr.soft** (see below) to run rr inside a Linux VM on Apple Silicon without hardware performance counters. (Source: rr-project.org, re-verified 2026-07-11: 5.9.0 remains the latest release.)

**Latest version**: 5.9.0 (Feb 2024). Key change: now works with `perf_event_paranoid=2` (the default on most distros) when the host kernel is ≥ 6.10. Version 5.8.0 added `lldb` support alongside the traditional gdb integration.

```bash
# Record a program execution
rr record ./my-binary --arg

# Replay with gdb (reverse-execution fully supported)
rr replay
(gdb) reverse-continue    # run backward to previous event
(gdb) reverse-next        # step backward one source line
(gdb) watch -l myvar      # hardware watchpoint — reverse-continue to when it last changed

# Replay with lldb (forward-only; added in rr 5.8.0)
rr replay -d lldb
```

```bash
# Record a specific PID (e.g., an already-running process)
rr record -p <PID>

# List available recordings
rr ls

# Replay the most recent recording
rr replay -d gdb
```

**rr.soft — software-counter mode**: For environments without CPU hardware performance counters (cloud VMs, Linux VMs on Apple Silicon macOS), [rr.soft](https://github.com/sidkshatriya/rr.soft) provides software-instrumented record/replay. Invoke with `rr record -W ./my-binary`. Supports both x86-64 and AArch64 Linux.

**CI integration**: Run flaky tests under `rr record`; on failure, upload the recording artifact and replay it locally to debug without re-flaking.

**Note**: rr adds some overhead during recording (typically 1.2–2×). It is not suitable for production; use it in a staging/CI environment. Some workloads that use unusual kernel interfaces or hardware features are not supported — check the rr FAQ if a recording fails.

---

## Pernosco — Omniscient Debugging on top of rr

**When to reach for it**: When rr replay + gdb is still too slow to navigate (stepping through millions of events), or when multiple engineers need to share and annotate a debugging session. Pernosco builds an omniscient database over an rr recording, enabling instant time-travel to any CPU state without re-executing.

**Platform**: x86-64 Linux programs that work with rr. Targets C, C++, Ada, Rust, and V8 JS. (Source: pernos.co, re-verified 2026-07-11: no status change found.)

**Workflow**:

1. Record with `rr record ./my-binary`.
2. Submit the recording to Pernosco (`pernosco submit`).
3. Open the session in a browser — navigate forward and backward in time, inspect any variable at any point, set reverse watchpoints, and leave notebook annotations.

**Availability**: Free for approved open-source projects (via GitHub Actions integration); hosted and on-premises plans for teams. Pernosco also sponsors rr development.

**When rr alone suffices vs. when to add Pernosco**:

| Situation | Use |
|-----------|-----|
| Single-engineer, < few thousand replay events | `rr replay` + gdb |
| Complex multi-threaded execution, many hours of replay | Pernosco for instant jump-to-event |
| Team needs to share or annotate a session | Pernosco notebook |
| CI failure needs offline async analysis | Pernosco (upload artifact once, replay any time) |

---

## Tool Selection Cheat Sheet

| Symptom | First reach for |
|---------|-----------------|
| Silent failure, no logs | `strace -e trace=file` |
| Port conflict or FD leak | `lsof -i :<port>` or `lsof -p <PID>` |
| CPU hotspot (Linux) | `perf top` → `perf record/report` |
| Production tracing, no recompile | `bpftrace` one-liner or BCC `opensnoop`/`execsnoop` |
| Kubernetes auto-instrumentation | Pixie or Beyla |
| Native crash / core dump (Apple) | `lldb -c core.dump` |
| Native crash / core dump (Linux) | `gdb ./binary core` |
| macOS syscall / Obj-C tracing | `dtrace` or `fs_usage` |
| Heisenbug / flaky CI failure | `rr record` → `rr replay` |
| Heisenbug in cloud VM or Apple Silicon Linux VM | `rr record -W` (rr.soft software-counter mode) |
| Complex trace, team sharing needed | Pernosco on top of an rr recording |
