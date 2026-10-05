# GPU Node and Cluster Tuning: Decision Criteria

Decision-oriented companion to [infrastructure-tuning.md](infrastructure-tuning.md). That file lists *what to set*; this one covers *when a setting is the right call*, what it trades away, and which anti-patterns silently cost bandwidth or tail latency.

Primary source: Chris Fregly, *AI Systems Performance Engineering* (O'Reilly, Nov 2025), Chapter 3 — "OS, Docker, and Kubernetes Tuning for GPU-Based Environments". Cited below as **[Fregly Ch 3]**.

Values that are generation-bound (MIG profile tables, NVLink domain bandwidth, minimum driver branches, SM counts) are called out as such rather than quoted as durable facts — verify against current NVIDIA docs for your SKU.

## Table of Contents

- [Scope: What This File Decides](#scope-what-this-file-decides)
- [NUMA Affinity: Resolve, Then Bind](#numa-affinity-resolve-then-bind)
- [Host Tuning Decision Table](#host-tuning-decision-table)
- [MPS vs MIG: The Central Decision](#mps-vs-mig-the-central-decision)
- [Clocks, Power Limits, and ECC](#clocks-power-limits-and-ecc)
- [Container Layer: Compatibility and I/O](#container-layer-compatibility-and-io)
- [Kubernetes: Topology-Aware Allocation](#kubernetes-topology-aware-allocation)
- [Kubernetes: Isolation and Jitter](#kubernetes-isolation-and-jitter)
- [Monitoring Hook: DCGM](#monitoring-hook-dcgm)
- [Anti-Patterns](#anti-patterns)

## Scope: What This File Decides

Reach for this file when the serving stack is already chosen and the remaining variance is coming from below the runtime: unexplained p99 spikes, GPUs that will not reach full utilization, multi-GPU jobs that get half the interconnect bandwidth they should, or pods dying to the OOM killer mid-run.

Node-level tuning does not fix a wrong batching policy or a wrong parallelism plan. Confirm the runtime-level levers first (see the SKILL.md decision flow), then come here.

## NUMA Affinity: Resolve, Then Bind

The mechanic is stable across generations: a process on a CPU in one NUMA node reaching a GPU or memory in another crosses an interconnect hop. **[Fregly Ch 3]** describes local node memory latency around ~80 ns with remote access roughly doubling it — treat the ratio as the durable point, not the nanoseconds.

Two-step pattern, in this order:

1. **Resolve** the GPU's NUMA node programmatically, not by hardcoding. Prefer NVML (`nvmlDeviceGetNUMANodeId`), fall back to `nvidia-smi topo -m`'s NUMA Affinity column, then to sysfs at `/sys/bus/pci/devices/<pci_id>/numa_node`. Hardcoded node IDs break the moment the fleet gains a differently-wired SKU.
2. **Bind** CPU *and* memory to that node together — `numactl --cpunodebind=N --membind=N`. Binding CPUs without `--membind` leaves the allocator free to serve pages from the far node, which negates the pinning entirely.

Two failure modes worth naming:

- **Linux auto-NUMA-balancing is not sufficient** for latency-sensitive work. It migrates processes across nodes on its own schedule. Bind explicitly. **[Fregly Ch 3]**
- **Workers spawned after binding do not reliably inherit the policy.** Dataloader and serving worker processes created post-fork should reapply and verify the binding inside the worker, not assume it propagated.

For pinned/page-locked host buffers, raise `ulimit -l` (max locked memory) to a high value or unlimited — a low limit makes pinning fail and silently falls back to swappable memory. **[Fregly Ch 3]**

## Host Tuning Decision Table

| Lever | Set it when | Leave it alone when | Cost of getting it wrong |
|---|---|---|---|
| Transparent hugepages (THP) | Throughput-bound work (training, high-batch offline inference) — THP reduces TLB pressure and page faults for large allocations | **Latency-sensitive online inference** — THP background compaction introduces unpredictable pauses. Prefer `transparent_hugepage=never` or `madvise` and manage explicit hugepages | Enabling THP on a latency-SLO serving node buys a few percent throughput and pays for it in p99 stalls |
| Explicit hugepages (`vm.nr_hugepages` / hugetlbfs) | Very large preallocated pinned I/O buffers, where deterministic behavior beats convenience | Ordinary workloads that THP already covers | Extra operational complexity for no gain |
| `vm.swappiness=0` | Always on a GPU node | Never — there is no case for swapping a GPU serving host | Any swapped page turns into a multiple-orders-of-magnitude stall **[Fregly Ch 3]** |
| CPU governor `performance` + shallow C-states | Latency-sensitive serving; benchmark rigs | Cost/power-constrained batch nodes where wake latency is amortized | Deep C-state wake latency shows up as unexplained request-level jitter |
| IRQ affinity pinned to the device's local node | GPU/NIC interrupt volume is material — multi-node, RDMA, high-QPS | Single-GPU dev boxes | Remote-node interrupt handling forces cache-coherency traffic and evicts useful lines |
| Core isolation (`isolcpus`, `nohz_full`, cpuset cgroups) | Dedicated dataloader/serving threads on a shared node | A node fully dedicated to one job | Background kernel work preempts the threads feeding the GPU |
| Real-time FIFO/RR priority on feeder threads | Rarely — only after core pinning has proven insufficient | Threads already pinned to dedicated cores | RT threads can starve other processes; **[Fregly Ch 3]** advises caution |
| Host allocator tuning (jemalloc/tcmalloc) | CPU-side allocation pauses are visibly stalling the GPU (utilization dips that are not synchronization barriers) | GPU utilization is already flat near saturation | Allocator lock contention and fragmentation appear as random data-prep latency |
| GPU persistence mode (`nvidia-persistenced`) | Effectively always on a serving fleet; **required in practice when MIG is configured** so slices survive idle periods | Nowhere meaningful | First CUDA call after idle stalls on driver reinitialization |

Allocator knobs from **[Fregly Ch 3]**: jemalloc via `MALLOC_CONF` (per-CPU `narenas`, `background_thread:true`, longer `dirty_decay_ms`/`muzzy_decay_ms`); tcmalloc via `TCMALLOC_MAX_TOTAL_THREAD_CACHE_BYTES` and `TCMALLOC_RELEASE_RATE`. Both are tuned to the workload — the point is larger per-thread caches and less eager return of freed pages, not the specific numbers.

**Containers inherit these from the host.** A container cannot change hugepage settings, the CPU governor, or sysctls. If the host image is untuned, no pod spec rescues it — fix it in the base OS image or via the GPU Operator's node-level configuration. **[Fregly Ch 3]**

## MPS vs MIG: The Central Decision

Both share one physical GPU across workloads. They are not interchangeable — they answer different questions.

- **MPS** (Multi-Process Service) merges multiple processes' work into a shared GPU context so kernels from different processes execute *concurrently* rather than time-sliced. Compute sharing, software-level.
- **MIG** (Multi-Instance GPU) partitions the GPU in *hardware* into fixed instances with their own SMs, memory slice, and engine contexts. Each instance looks like a separate GPU.

| Criterion | MPS | MIG |
|---|---|---|
| Isolation strength | None for memory — all clients share the full GPU memory space. A misbehaving client can OOM its neighbors | Hardware-isolated SMs and memory; a fault in one instance does not take out others |
| Memory partitioning | No | Yes, fixed per profile |
| Compute control | `CUDA_MPS_ACTIVE_THREAD_PERCENTAGE` caps a client's share of SMs | Fixed by the chosen profile |
| Best for | Many small inference jobs that each under-saturate the GPU; bursty kernels with idle gaps to overlap | Multiple independent tenants/jobs on one GPU where isolation is a requirement |
| Reconfiguration cost | Start/stop a daemon | Enabling or disabling MIG *mode* requires a GPU reset (or node reboot); creating/destroying instances requires draining workloads |
| Multi-tenancy | Modern drivers support multi-user MPS, but this improves usability only — **it does not add memory isolation** | The isolation answer |
| Granularity | Continuous (thread percentage) | Discrete, fixed profiles per generation; unused slices are stranded capacity |
| **NVLink / P2P** | Unaffected | **Disabled while the GPU is in MIG mode** — no NVLink or PCIe peer-to-peer across GPUs, and CUDA IPC across instances is limited. Traffic must route through host memory or the network |
| Kubernetes surface | Node-level daemon setup | Device plugin advertises slices as distinct resources (e.g. `nvidia.com/mig-<profile>`) |
| Scheduling constraint | None specific | A pod's MIG requests must be satisfiable **on one node** — pods cannot span nodes, so a request stays `Pending` even when the cluster has enough MIG capacity spread across nodes |

**Decision rule.** Ask two questions in order:

1. *Does any workload on this GPU need isolation guarantees — separate tenants, a blast-radius boundary, or a hard memory ceiling?* If yes → MIG. If no, continue.
2. *Does a single workload already saturate the GPU?* If yes → neither helps; MPS cannot manufacture headroom that does not exist **[Fregly Ch 3]**. If no → MPS, to overlap the idle gaps.

**Do not enable MIG on nodes running large distributed training or multi-GPU collective-heavy inference** (tensor-parallel serving, sparse-MoE expert routing). Losing NVLink peer-to-peer is the dominant cost and it dwarfs any packing benefit. **[Fregly Ch 3]** A common cluster pattern is labeling nodes `mig-enabled` / `mig-disabled` and routing jobs by label, rather than trying to flip modes per job — MIG is a static partition, not a dynamic scheduler product.

Plain **time-slicing** (the device plugin's oversubscription mode) is a third option that needs no MPS daemon, but it interleaves rather than overlapping execution — acceptable for low-duty-cycle jobs, worse than MPS or MIG for throughput. **[Fregly Ch 3]**

MIG profile tables (SM fraction, memory per slice, decoder counts) are **fixed per GPU generation and type**. Read the current profile table for the exact SKU; do not carry numbers across generations.

## Clocks, Power Limits, and ECC

| Setting | When it earns its place | Tradeoff |
|---|---|---|
| Locked core/memory clocks (`nvidia-smi -lgc`, `-ac`) | **Benchmarking and A/B comparisons** — GPU Boost varies clocks with power/thermal headroom, so an unlocked GPU makes run-to-run deltas uninterpretable | In production, locking forfeits opportunistic boost; only worth it when run-to-run consistency is the goal |
| Power limit (`nvidia-smi -pl`) below TDP | Thermally constrained racks, or deliberately trading peak throughput for lower heat and steadier clocks | Boost auto-adjusts clocks downward — you are choosing consistency over peak |
| ECC disabled | Effectively never for serious workloads | Frees a small amount of memory and yields a few percent at best, while removing detection of memory corruption. Toggling requires a GPU reset. **[Fregly Ch 3]**: keep ECC on |

## Container Layer: Compatibility and I/O

**The split that makes GPU containers work.** The host owns the NVIDIA driver (kernel-integrated); the container image carries the CUDA runtime libraries. The NVIDIA Container Toolkit injects the host's driver libraries (`libcuda.so`, `libnvidia-ml.so`) into the container at start, while the app uses the image's `libcudart.so`. No hypervisor is involved — containers share the host kernel, so GPU work runs at effectively bare-metal speed. **[Fregly Ch 3]**

**The compatibility rule:** the host driver must be at least as recent as the minimum branch required by the CUDA version *inside* the container. A newer container CUDA on an older host driver fails at CUDA initialization. Minimum driver branches are version-bound — check NVIDIA's current compatibility matrix rather than memorizing a pairing.

**PTX vs CUBIN — why a build can fail on new hardware.** `nvcc` emits a fatbinary containing architecture-specific CUBIN plus intermediate PTX. CUBIN runs directly on known architectures and is **not forward-compatible**; PTX lets the driver JIT-compile for architectures that did not exist at build time. Ship fat binaries with PTX embedded if the image must run on future GPUs — otherwise a new SKU rollout produces "no kernel image is available" failures. The tradeoff: the first launch on a new architecture pays JIT compilation latency, which matters for cold-start-sensitive serving.

**OverlayFS.** The union filesystem must consult multiple layers to resolve a file, and copy-on-write copies a file into the writable layer before the first modification. For model weights, datasets, and checkpoint writes, this overhead is avoidable:

- Bind-mount weights and data from the host (`-v /host/models:/mnt/models:ro`) — bind mounts bypass the overlay and perform like host disk I/O.
- Never bake multi-gigabyte weights into the image; bring them in via mount.
- Avoid heavy reads/writes against the container's writable layer.

**Image size** matters for startup, not steady state. For long-running training the pull time is negligible; for autoscaled inference replicas it is directly in the cold-start path — trim build tools and intermediate artifacts. The Container Toolkit works with containerd and Podman, not only Docker.

## Kubernetes: Topology-Aware Allocation

**Kubernetes is not topology-aware by default.** It treats GPUs as fungible countable resources with no knowledge of which share a NUMA node or an NVLink domain. **[Fregly Ch 3]**

**The anti-pattern, concretely.** On a node whose GPUs form two NVLink-connected groups, a request for 4 GPUs can be satisfied by two GPUs from each group. The job now routes GPU-to-GPU traffic over the slower fabric (PCIe/InfiniBand/Ethernet) instead of NVLink, which can halve effective inter-GPU bandwidth — for a collective-heavy workload that is a direct throughput loss, invisible in the pod spec and easy to misdiagnose as a framework problem. The same failure scales up: on rack-scale NVLink domains, a non-topology-aware scheduler can place a job across domains and forfeit the entire point of the rack.

The stack that prevents it:

| Component | What it contributes |
|---|---|
| NVIDIA device plugin | Advertises GPUs to the scheduler and mounts device nodes into pods; topology-aware — can prefer GPUs sharing an NVLink switch or NUMA node |
| GPU Operator | Installs and lifecycles driver, device plugin, and Container Toolkit; can enforce persistence mode and node-level sysctls; runs the MIG Manager so partitions survive reboots and driver reloads |
| GPU Feature Discovery / Node Feature Discovery | Labels each GPU with NUMA node and NVLink/NVSwitch ID so the scheduler can act on topology |
| Topology Manager | Aligns the container's CPU allocation with the NUMA node of its allocated GPUs — `--topology-manager-policy` of `best-effort`, `restricted`, or `single-numa-node` |

Policy choice is a strictness dial: `best-effort` never blocks scheduling but gives no guarantee; `restricted` and `single-numa-node` refuse misaligned placements, trading schedulability for predictability. Pick `single-numa-node` only when you have enough aligned capacity for pods to actually schedule.

Topology-aware GPU scheduling is still maturing **[Fregly Ch 3]** — many clusters supplement it with explicit node labels and selectors. Where the workload is latency-critical and the node count allows it, requesting the *whole node* is the reliable version of topology awareness.

**Networking.** For multi-node work, the pod overlay network and NAT add overhead. `hostNetwork: true` gives the container the host's interfaces directly, which is the simplest path to InfiniBand access and removes per-rank port mapping for MPI jobs. Where security policy forbids host networking, the CNI must carry the traffic in kernel space with no user-space proxy throttling, and NCCL needs its ports reachable (`NCCL_SOCKET_IFNAME`, `NCCL_PORT_RANGE`). For RDMA, install the RDMA device plugin to expose InfiniBand and GPUDirect RDMA endpoints, and enable GPUDirect RDMA in the driver so GPUs exchange data with the NIC without a CPU bounce.

## Kubernetes: Isolation and Jitter

**QoS class is the lever, not the limit value.** A pod with no requests/limits is `BestEffort` and the first thing evicted. Setting a high limit alone yields `Burstable`. **Guaranteed** requires `requests == limits` for CPU *and* memory on *every* container in the pod. **[Fregly Ch 3]** This is the single most common misconfiguration in the list — teams set a generous limit, believe they reserved capacity, and get Burstable.

**The OOM-killer tradeoff, stated honestly.** The kernel OOM killer uses heuristics that often target the largest process — frequently your inference server holding host-side batch data. **[Fregly Ch 3]** offers two defensible postures:

- Set memory limits comfortably *above* real expected usage, so headroom absorbs spikes without inviting a kill three days in.
- Or deliberately omit strict memory limits so the container can use available memory, and rely on monitoring and alerting to catch over-allocation.

The second gives up Guaranteed QoS. Choose per node: on a dedicated node the second is workable; on a shared node the first is safer, because an unbounded neighbor can push the *host* into swap and get your pod killed for someone else's allocation.

**Jitter sources and their fixes:**

- Co-tenancy of training and inference on one node is the worst case — **[Fregly Ch 3]** notes homogeneous workloads are markedly easier to tune and debug. Separate them by node pool where possible.
- CPU contention: use requests plus the CPU Manager's static policy to pin cores so nothing else is scheduled on them.
- Interrupts from neighboring pods' network and disk traffic — same IRQ-affinity remedy as the host section, plus cgroup partitioning.
- **I/O has no first-class Kubernetes isolation.** CPU and memory are handled; I/O is not. If heavy I/O neighbors matter, configure the cgroup v2 I/O controller at the node level manually. **[Fregly Ch 3]**

The ideal, where the budget allows: a performance-sensitive job requests all CPUs and GPUs on its node.

## Monitoring Hook: DCGM

DCGM (Data Center GPU Manager) is the fleet-level GPU metrics and health layer, and the GPU Operator deploys it as part of the standard stack **[Fregly Ch 3]**. Treat it as the source for per-GPU utilization, memory, clocks/throttle reasons, ECC events, and NVLink traffic — the signals that tell you whether a node-tuning change actually landed.

Node tuning without DCGM in place is unfalsifiable. Before changing any lever above, confirm you can see the metric it is supposed to move — throttle-reason counters for the clock/power work, NVLink counters for the topology work, utilization traces for the affinity and allocator work. Route alerting and SLO design to [qa-observability](../../qa-observability/SKILL.md); this section only establishes DCGM as the collection point.

## Anti-Patterns

- **Enabling THP on a latency-SLO inference node.** Compaction pauses land directly in p99. THP is a throughput setting.
- **Binding CPUs without binding memory.** `--cpunodebind` alone leaves allocation free to cross nodes; the pinning buys nothing.
- **Hardcoding a GPU's NUMA node.** Resolve it at runtime via NVML or sysfs; hardcoded IDs break on the next SKU.
- **Reaching for MPS when one workload already saturates the GPU.** There is no idle time to overlap.
- **Enabling MIG on collective-heavy nodes.** Losing NVLink P2P costs more than the packing gains.
- **Requesting N GPUs and assuming they share an NVLink domain.** Without topology labels and Topology Manager, they often do not — and the loss shows up as a framework mystery.
- **Setting a high memory limit and believing it is Guaranteed QoS.** Guaranteed requires `requests == limits` on every container.
- **Shipping CUBIN-only images.** Works until a new GPU generation arrives, then fails at launch. Embed PTX.
- **Baking model weights into the container image.** Pays OverlayFS CoW cost and inflates cold start; bind-mount instead.
- **Tuning inside the container.** Hugepages, governor, and sysctls are host-level; fix the node image.
- **Benchmarking on unlocked clocks.** GPU Boost varies with thermal headroom, so the deltas you measure are partly ambient temperature.

## Related

- [infrastructure-tuning.md](infrastructure-tuning.md) — the command-level checklist for these same layers
- [gpu-optimization-checklists.md](gpu-optimization-checklists.md) — hardware fit and production tuning
- [parallelism-patterns.md](parallelism-patterns.md) — why NVLink-domain placement matters for TP/EP
- [profiling-and-capacity-planning.md](profiling-and-capacity-planning.md) — measuring before and after these changes
