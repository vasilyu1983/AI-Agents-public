# Memory Leak Detection

Patterns and tools for detecting, diagnosing, and resolving memory leaks across languages and runtime environments, from development profiling to production monitoring.

---

## Contents

- [Memory Leak Fundamentals](#memory-leak-fundamentals)
- [Common Leak Patterns](#common-leak-patterns)
- [Node.js Memory Profiling](#nodejs-memory-profiling)
- [Python Memory Profiling](#python-memory-profiling)
- [Browser Memory Debugging](#browser-memory-debugging)
- [C/C++ Memory Analysis](#cc-memory-analysis)
- [Garbage Collection Analysis](#garbage-collection-analysis)
- [Memory Growth Trending](#memory-growth-trending)
- [Production Memory Monitoring](#production-memory-monitoring)
- [Container Memory Limits and OOM](#container-memory-limits-and-oom)
- [Remediation Patterns](#remediation-patterns)
- [Memory Leak Detection Checklist](#memory-leak-detection-checklist)
- [Related Resources](#related-resources)

---

## Memory Leak Fundamentals

A memory leak occurs when allocated memory is no longer needed but is not released, causing unbounded growth over time.

| Language | Leak Mechanism | Primary Tool |
|----------|---------------|-------------|
| JavaScript (Node.js) | Retained references, closures, event listeners | `--inspect` + Chrome DevTools |
| JavaScript (Browser) | Detached DOM, closures, Web Workers | Chrome DevTools Memory tab |
| Python | Circular references, global accumulators, C extensions | memray, objgraph, tracemalloc |
| Java/Kotlin | Static collections, unclosed resources, classloader leaks | VisualVM, Eclipse MAT |
| Go | Goroutine leaks, global maps, pprof | `pprof`, `runtime.ReadMemStats` |
| C/C++ | Malloc without free, dangling pointers | Valgrind, AddressSanitizer |
| Rust | Reference cycles with Rc/Arc | Does not typically leak (ownership model) |

---

## Common Leak Patterns

### Pattern 1: Event Listener Accumulation

```javascript
// LEAK: Adding listeners without removing them
class DataStream {
  constructor(emitter) {
    // Each call adds a NEW listener that is never removed
    emitter.on('data', (chunk) => {
      this.process(chunk);
    });
  }
}
// Fix: Store reference and remove on cleanup
class DataStream {
  constructor(emitter) {
    this.handler = (chunk) => this.process(chunk);
    emitter.on('data', this.handler);
  }
  destroy() {
    this.emitter.removeListener('data', this.handler);
  }
}
```

### Pattern 2: Closure Capturing Outer Scope

```javascript
// LEAK: Closure retains reference to large object
function processLargeData() {
  const largeBuffer = Buffer.alloc(100 * 1024 * 1024); // 100MB

  return function getStatus() {
    // Closure captures entire scope, keeping largeBuffer alive
    return 'done';
  };
}

// Fix: Null out references or restructure
function processLargeData() {
  let largeBuffer = Buffer.alloc(100 * 1024 * 1024);
  const result = transform(largeBuffer);
  largeBuffer = null; // Allow GC
  return function getStatus() { return result; };
}
```

### Pattern 3: Global Accumulator

```python
# LEAK: Cache grows without bound
_cache = {}

def get_user(user_id: str):
    if user_id not in _cache:
        _cache[user_id] = fetch_from_db(user_id)
    return _cache[user_id]

# Fix: Use bounded cache
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user(user_id: str):
    return fetch_from_db(user_id)
```

### Pattern 4: Circular References

```python
# LEAK: Circular reference prevents reference counting cleanup
class Node:
    def __init__(self):
        self.parent = None
        self.children = []

    def add_child(self, child):
        child.parent = self      # parent -> child -> parent cycle
        self.children.append(child)

# Fix: Use weak references for back-references
import weakref

class Node:
    def __init__(self):
        self._parent = None
        self.children = []

    @property
    def parent(self):
        return self._parent() if self._parent else None

    def add_child(self, child):
        child._parent = weakref.ref(self)
        self.children.append(child)
```

### Leak Pattern Summary

| Pattern | Language | Detection Signal | Fix |
|---------|----------|-----------------|-----|
| Event listener accumulation | JS | MaxListenersExceeded warning | Remove on destroy/unmount |
| Closure scope capture | JS | Large retained size in heap | Null out references |
| Global cache/map growth | Any | Monotonically increasing object count | Bounded cache (LRU) |
| Circular references | Python | GC generation 2 growth | Weak references |
| Detached DOM nodes | Browser | Nodes in heap but not in tree | Remove references |
| Unclosed resources | Java/Python | File descriptors, connections grow | Context managers, try-with-resources |
| Goroutine leaks | Go | Goroutine count grows | Context cancellation |

---

## Node.js Memory Profiling

### Heap Snapshot with --inspect

```bash
# Start Node.js with inspector
node --inspect app.js

# Or attach to running process
kill -USR1 <pid>  # Enable inspector on running process
```

Then connect Chrome DevTools to `chrome://inspect`.

### Programmatic Heap Snapshots

```javascript
const v8 = require('v8');
const fs = require('fs');

function takeHeapSnapshot(label) {
  const filename = `heap-${label}-${Date.now()}.heapsnapshot`;
  const snapshotStream = v8.writeHeapSnapshot();
  console.log(`Heap snapshot written to ${snapshotStream}`);
  return snapshotStream;
}

// Take snapshots at intervals to compare
setInterval(() => {
  const used = process.memoryUsage();
  console.log(`RSS: ${(used.rss / 1024 / 1024).toFixed(1)}MB, ` +
              `Heap: ${(used.heapUsed / 1024 / 1024).toFixed(1)}MB`);

  if (used.heapUsed > 500 * 1024 * 1024) { // Over 500MB
    takeHeapSnapshot('high-memory');
  }
}, 30000);
```

### Memory Usage Monitoring Endpoint

```javascript
const express = require('express');
const app = express();

app.get('/debug/memory', (req, res) => {
  const mem = process.memoryUsage();
  res.json({
    rss_mb: (mem.rss / 1024 / 1024).toFixed(2),
    heap_total_mb: (mem.heapTotal / 1024 / 1024).toFixed(2),
    heap_used_mb: (mem.heapUsed / 1024 / 1024).toFixed(2),
    external_mb: (mem.external / 1024 / 1024).toFixed(2),
    array_buffers_mb: (mem.arrayBuffers / 1024 / 1024).toFixed(2),
  });
});
```

---

## Python Memory Profiling

### Using tracemalloc (stdlib)

```python
import tracemalloc

# Start tracing
tracemalloc.start()

# ... run workload ...

# Take snapshot
snapshot = tracemalloc.take_snapshot()

# Top 10 memory consumers by file
top_stats = snapshot.statistics('lineno')
print("[ Top 10 Memory Consumers ]")
for stat in top_stats[:10]:
    print(f"  {stat}")

# Compare two snapshots to find growth
snapshot1 = tracemalloc.take_snapshot()
# ... more work ...
snapshot2 = tracemalloc.take_snapshot()

top_diffs = snapshot2.compare_to(snapshot1, 'lineno')
print("[ Top Memory Growth ]")
for stat in top_diffs[:10]:
    print(f"  {stat}")
```

### Using memray (Recommended for Production Profiling)

```bash
# Install
pip install memray

# Profile a script
memray run my_script.py

# Profile with live view
memray run --live my_script.py

# Generate flamegraph from results
memray flamegraph output.bin -o flamegraph.html

# Show top allocations
memray summary output.bin

# Attach to running process
memray attach <pid>
```

### Using objgraph (Object Reference Analysis)

```python
import objgraph

# Show most common types
objgraph.show_most_common_types(limit=20)

# Show objects that grew since last call
objgraph.show_growth(limit=10)

# Find what references a specific object
objgraph.show_backrefs(
    objgraph.by_type('MyLeakyClass')[:3],
    max_depth=5,
    filename='refs.png',
)
```

---

## Browser Memory Debugging

### Chrome DevTools Memory Tab Workflow

```text
1. Open DevTools → Memory tab
2. Select "Heap snapshot"
3. Take Snapshot #1 (baseline)
4. Perform suspected leaking action (e.g., open/close modal 10 times)
5. Take Snapshot #2
6. Select Snapshot #2, choose "Comparison" view
7. Sort by "# Delta" to find growing object types
8. Expand to inspect retained references
```

### Detached DOM Node Detection

```javascript
// In Chrome DevTools Console:
// Find detached DOM elements still in memory

// Method 1: DevTools Heap Snapshot
// Filter by "Detached" in the heap snapshot viewer

// Method 2: Performance Monitor
// DevTools → More tools → Performance Monitor
// Watch "DOM Nodes" and "JS Heap" counters

// Method 3: Manual check
function checkDetachedNodes() {
  const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      console.log('DOM nodes:', performance.memory?.usedJSHeapSize);
    }
  });

  // Create and remove elements, check if count returns to baseline
  const baseline = document.querySelectorAll('*').length;
  // ... perform action ...
  const after = document.querySelectorAll('*').length;
  console.log(`DOM delta: ${after - baseline}`);
}
```

### React-Specific Leak Patterns

```javascript
// LEAK: useEffect without cleanup
function ChatRoom({ roomId }) {
  useEffect(() => {
    const connection = createConnection(roomId);
    connection.connect();
    // Missing cleanup: connection stays open forever
  }, [roomId]);
}

// FIX: Return cleanup function
function ChatRoom({ roomId }) {
  useEffect(() => {
    const connection = createConnection(roomId);
    connection.connect();
    return () => connection.disconnect(); // Cleanup on unmount
  }, [roomId]);
}

// LEAK: setInterval without clearInterval
function Timer() {
  const [count, setCount] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setCount(c => c + 1), 1000);
    // Missing: clearInterval(id)
  }, []);
}
```

---

## C/C++ Memory Analysis

### Valgrind

```bash
# Detect memory leaks
valgrind --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         --verbose \
         ./my_program

# Output summary
# ==12345== LEAK SUMMARY:
# ==12345==    definitely lost: 48 bytes in 3 blocks
# ==12345==    indirectly lost: 0 bytes in 0 blocks
# ==12345==      possibly lost: 0 bytes in 0 blocks
# ==12345==    still reachable: 200 bytes in 1 blocks
```

### AddressSanitizer (ASan)

```bash
# Compile with ASan
gcc -fsanitize=address -g my_program.c -o my_program

# Run (ASan reports leaks on exit)
ASAN_OPTIONS=detect_leaks=1 ./my_program

# With more detail
ASAN_OPTIONS="detect_leaks=1:print_stats=1:log_path=asan.log" ./my_program
```

---

## Garbage Collection Analysis

### Node.js GC Tracing

```bash
# Enable GC logging
node --trace-gc app.js

# Verbose GC output
node --trace-gc --trace-gc-verbose app.js

# Expose GC for manual triggering
node --expose-gc app.js
```

```javascript
// Programmatic GC monitoring
const { PerformanceObserver } = require('perf_hooks');

const obs = new PerformanceObserver((items) => {
  items.getEntries().forEach((entry) => {
    if (entry.entryType === 'gc') {
      console.log(`GC: ${entry.detail.kind} took ${entry.duration.toFixed(1)}ms`);
    }
  });
});
obs.observe({ entryTypes: ['gc'] });
```

### Python GC Debugging

```python
import gc

# Enable GC debugging
gc.set_debug(gc.DEBUG_STATS | gc.DEBUG_LEAK)

# Force collection and inspect uncollectable
gc.collect()
print(f"Uncollectable objects: {len(gc.garbage)}")

# Inspect generation counts
print(f"Generation counts: {gc.get_count()}")
print(f"Thresholds: {gc.get_threshold()}")
```

---

## Memory Growth Trending

### Automated Growth Detection

```python
import time
import statistics

def detect_memory_growth(
    get_memory_fn,
    sample_interval: float = 5.0,
    window_size: int = 60,
    growth_threshold_mb: float = 10.0,
) -> dict:
    """Monitor memory over time and detect sustained growth."""
    samples = []

    for _ in range(window_size):
        memory_mb = get_memory_fn() / (1024 * 1024)
        samples.append(memory_mb)
        time.sleep(sample_interval)

    # Linear regression to detect trend
    n = len(samples)
    x_mean = (n - 1) / 2
    y_mean = statistics.mean(samples)
    numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(samples))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator else 0

    growth_per_hour = slope * (3600 / sample_interval)

    return {
        "start_mb": round(samples[0], 1),
        "end_mb": round(samples[-1], 1),
        "growth_mb": round(samples[-1] - samples[0], 1),
        "growth_per_hour_mb": round(growth_per_hour, 1),
        "is_leaking": growth_per_hour > growth_threshold_mb,
        "sample_count": n,
    }
```

### Prometheus Metrics for Memory

```python
from prometheus_client import Gauge, Histogram
import psutil
import os

process_memory_rss = Gauge(
    'process_memory_rss_bytes',
    'Resident Set Size in bytes',
)
process_memory_heap = Gauge(
    'process_memory_heap_bytes',
    'Heap memory used in bytes',
)

def update_memory_metrics():
    process = psutil.Process(os.getpid())
    mem = process.memory_info()
    process_memory_rss.set(mem.rss)
    process_memory_heap.set(mem.vms)
```

---

## Production Memory Monitoring

### Alert Rules (Prometheus)

```yaml
# prometheus_rules.yml
groups:
  - name: memory_alerts
    rules:
      - alert: MemoryLeakSuspected
        expr: |
          deriv(process_memory_rss_bytes[1h]) > 10 * 1024 * 1024
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Possible memory leak in {{ $labels.instance }}"
          description: "RSS growing >10MB/hour for 30 minutes"

      - alert: HighMemoryUsage
        expr: |
          process_memory_rss_bytes / on(instance) node_memory_MemTotal_bytes > 0.85
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
```

### Key Metrics to Monitor

| Metric | Warning Threshold | Critical Threshold | Notes |
|--------|------------------|-------------------|-------|
| RSS growth rate | > 10MB/hour | > 50MB/hour | Sustained over 30min |
| Heap usage | > 70% of limit | > 85% of limit | Per-process |
| GC pause time | > 100ms | > 500ms | p99 latency impact |
| GC frequency | > 10/min | > 30/min | Memory pressure signal |
| OOM kills | Any occurrence | - | Always investigate |
| Container memory | > 80% of limit | > 90% of limit | K8s resource limit |

---

## Container Memory Limits and OOM

### Kubernetes Memory Configuration

```yaml
# deployment.yaml
spec:
  containers:
    - name: api
      resources:
        requests:
          memory: "256Mi"
        limits:
          memory: "512Mi"   # OOM-killed if exceeded
      env:
        - name: NODE_OPTIONS
          value: "--max-old-space-size=400"  # Leave headroom below limit
```

### Diagnosing OOM Kills

```bash
# Check if pod was OOM-killed
kubectl describe pod <pod-name> | grep -A 5 "Last State"

# Check node-level OOM events
kubectl get events --field-selector reason=OOMKilling

# Check dmesg for kernel OOM killer
dmesg | grep -i "oom\|killed process"

# View container memory usage
kubectl top pod <pod-name> --containers
```

### OOM Prevention Strategies

- [ ] Set `--max-old-space-size` (Node.js) below container limit
- [ ] Set `-Xmx` (Java) below container limit
- [ ] Leave 15-20% headroom between application limit and container limit
- [ ] Monitor memory via metrics, not just container restarts
- [ ] Configure graceful shutdown on memory pressure signals

---

## Remediation Patterns

| Root Cause | Fix Pattern | Verification |
|-----------|-------------|-------------|
| Unbounded cache | LRU cache with max size | Size metric stays bounded |
| Event listener leak | Proper cleanup on destroy | Listener count stable |
| Closure retention | Null out large references | Heap snapshot comparison |
| Circular references | Weak references | GC collects properly |
| Connection pool growth | Pool size limits + idle timeout | Connection count bounded |
| Log buffer accumulation | Flush + rotate | Buffer size constant |
| Global state growth | Periodic cleanup + TTL | Object count stable |

---

## Memory Leak Detection Checklist

- [ ] Memory profiling tools installed and configured for your language/runtime
- [ ] Heap snapshots can be taken in dev and staging environments
- [ ] Common leak patterns reviewed against codebase (event listeners, closures, caches)
- [ ] Automated memory growth tests run in CI (load test + memory trend)
- [ ] GC behavior monitored and pauses tracked
- [ ] Production memory metrics exported (RSS, heap, GC stats)
- [ ] Alert rules configured for sustained memory growth
- [ ] Container memory limits set with appropriate headroom
- [ ] OOM kill events monitored and alerted
- [ ] Known leak patterns documented in team runbook
- [ ] Memory profiling is part of code review for data-heavy features

---

## Related Resources

- **[debugging-methodologies.md](debugging-methodologies.md)** - General debugging approaches
- **[production-debugging-patterns.md](production-debugging-patterns.md)** - Production debugging techniques
- **[race-condition-diagnosis.md](race-condition-diagnosis.md)** - Concurrency bug detection
- **[logging-best-practices.md](logging-best-practices.md)** - Logging for diagnostics
- **[SKILL.md](../SKILL.md)** - QA Debugging skill overview
