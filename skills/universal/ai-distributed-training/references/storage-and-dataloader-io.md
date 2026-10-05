# Storage I/O and Dataloader Pipeline Tuning

Distilled from Chris Fregly, *AI Systems Performance Engineering* (O'Reilly, Nov 2025), Chapter 5 — "GPU-Based Storage I/O Optimizations". Use this when a training run shows low MFU and profiling points at data starvation rather than compute or collectives.

## Table of Contents

- [The Core Failure Mode: Small Random Reads](#the-core-failure-mode-small-random-reads)
- [Storage Layer Tuning](#storage-layer-tuning)
- [GPUDirect Storage (GDS)](#gpudirect-storage-gds)
- [cuda-checkpoint (GPU State, Not Data Ingest)](#cuda-checkpoint-gpu-state-not-data-ingest)
- [Diagnosing a Dataloader-Bound Run](#diagnosing-a-dataloader-bound-run)
- [Dataloader Tuning Knobs](#dataloader-tuning-knobs)
- [GPU-Side Decode (NVIDIA DALI)](#gpu-side-decode-nvidia-dali)
- [Monitoring Toolchain](#monitoring-toolchain)
- [Continuous Profiling Workflow](#continuous-profiling-workflow)
- [Canonical Sources](#canonical-sources)

## The Core Failure Mode: Small Random Reads

Storage delivers far higher throughput on large sequential reads than on small random ones. Millions of individual sample files (one JPEG per image, one JSON per document) turn every epoch into a seek storm, and the faster the GPU, the sooner that seek storm becomes the binding constraint.

The fix is offline, not runtime: **shard many samples into a few large files** — Arrow, Parquet, TFRecord, WebDataset tar, or NeMo's memory-mappable `.bin`/`.idx` pairs. One chunked read then yields many samples. Same logic applies to object storage: concatenate small S3 objects into large ones before training starts.

| Symptom | Likely cause | Move |
|---------|-------------|------|
| High IOPS, low MB/s | Millions of small files | Shard into large sequential files |
| Read size ~4 KB | Untuned buffer / prefetch chunk | Raise read size toward ~1 MB chunks |
| Random access genuinely unavoidable | Per-syscall overhead dominates | Parallel `pread()` threads or `io_uring` (preregistered buffers, polling) |
| Network saturated by redundant reads | Every node reads the whole dataset | Pre-split shards to node-local NVMe; `DistributedSampler` per rank |
| Object store read directly per sample | Per-object latency | Stage to local NVMe, or cache layer (e.g. FSx for Lustre over S3); multithreaded range GETs via `s5cmd` |

Place data as physically close to compute as possible: node-local NVMe first, then rack-local NVMe-oF, then a parallel filesystem. If the dataset fits in RAM (or unified CPU+GPU memory), preload it at startup and skip disk entirely during training.

## Storage Layer Tuning

**NVMe / block layer.** Modern Linux uses the `blk-mq` multiqueue scheduler. Verify with `/sys/block/nvme*/queue/scheduler` — `none` (low-latency default) or `mq-deadline` are the right settings for high-performance NVMe; the legacy CFQ scheduler is obsolete. This is almost always correct out of the box, so treat it as a check, not a tuning project. Raise `read_ahead_kb` (`/sys/block/<dev>/queue/read_ahead_kb`, commonly 128 KB by default) to a few MB when streaming large files, via `blockdev --setra`. Confirm the SSDs sit on enough PCIe lanes; stripe multiple SSDs with RAID 0 if one disk cannot saturate the GPUs.

**Filesystem.** XFS is the common Linux NVMe choice. Mount with `noatime` to drop access-time writes on every read.

**NFS.** Viable only at modest scale — a few nodes. A single NFS server becomes a throughput bottleneck once many nodes read concurrently; parallel filesystems (Lustre, GPFS) or a cloud cache are the answer for real clusters. If NFS must be used: multiple fast NICs, dataset split across several servers, NVMe-backed storage, and tuned client mount options — max `rsize`/`wsize` (e.g. 1 MiB), `noatime`, `async`, plus `actimeo`/`lookupcache` to cache attributes and directory entries.

**Parallel filesystems.** Stripe large files across many Object Storage Targets so reads go parallel (`lfs setstripe` on Lustre). Monitor for hot storage nodes during training — a hot node almost always means a sharding imbalance concentrating reads.

**Replication vs compression.** Two opposite trades, both legitimate:

| Option | Buys | Costs | Pick when |
|--------|------|-------|-----------|
| Replicate dataset to every node | Eliminates network reads entirely | N× storage | Dataset fits node-local disk; network is the bottleneck |
| Store compressed, decompress on the fly | Less I/O bandwidth per sample | CPU/GPU cycles | I/O is the bottleneck and CPU/GPU have headroom |

Compression only helps while decompression does not become the new bottleneck. GPU-side decode paths reduce that risk: nvJPEG for images, and the on-die decompression engine on recent NVIDIA GPUs for LZ4/Snappy/Deflate — favor those formats for I/O-bound work.

## GPUDirect Storage (GDS)

**What it is.** Normally a GPU read goes SSD → host memory → (CUDA copy) → GPU memory. GDS creates a direct DMA path from storage or NIC into GPU HBM, removing the host bounce buffer. It is the storage-side counterpart of GPUDirect RDMA (network-to-GPU); neither removes CPU *orchestration*, only the host memory copy.

**Requirements** (categorical — verify specifics against current NVIDIA docs, this stack drifts):

- A supported NVIDIA GPU plus matching drivers, CUDA toolkit, and the `nvidia-fs` kernel driver.
- A storage stack with kernel-level integration and `O_DIRECT` semantics. Local NVMe and NVMe-oF on XFS/EXT4, NFS over RDMA, and select parallel filesystems (BeeGFS, WekaFS, VAST, IBM Storage Scale) are the documented paths.
- Application reads through CUDA's **cuFile** API (`cuFileRead`, plus `cuFileReadAsync` / `cuFileWriteAsync` for CUDA-stream overlap).
- A FUSE user-space filesystem **cannot** provide a GDS path — kernel-level `O_DIRECT` integration is required.

**When it applies.** Training is overwhelmingly read-heavy, so GDS gains are almost always measured on the read path. It helps most when the CPU is saturated moving data; if the CPU was comfortably handling transfers, GDS may not move throughput much but still frees CPU cycles for preprocessing. RDMA-accelerated checkpoint *writes* require filesystem support for GDS writes.

**Benchmark it before believing it.** `gdsio` (default `/usr/local/cuda/gds/tools`) measures both paths; keep the transfer selector consistent when comparing — `-x 2` is the CPU-mediated path, `-x 0` is the GDS path.

```bash
# CPU-mediated baseline (host memory, async copies)
/usr/local/cuda/gds/tools/gdsio -f /mnt/data/large_file -d 0 -w 4 -s 10G -i 1M -I 0 -x 2
# Same config through GDS
/usr/local/cuda/gds/tools/gdsio -f /mnt/data/large_file -d 0 -w 4 -s 10G -i 1M -I 0 -x 0
```

Fregly reports vendor measurements of roughly a 20% read-throughput uplift on A100 and 30%+ on H100, and notes uplift varies with I/O size, queue depth, NIC generation, and filesystem — measure on your own fabric rather than quoting these.

## cuda-checkpoint (GPU State, Not Data Ingest)

NVIDIA's `cuda-checkpoint`, paired with a CPU process checkpointer such as CRIU, snapshots a running CUDA process: it locks driver entry points, drains submitted work, copies device memory into driver-managed host allocations, and releases GPU resources. Restore reacquires GPUs, remaps device memory to original addresses, and rebuilds CUDA objects (streams, contexts); it needs persistence mode (or `cuInit`) and can remap to different physical GPUs of the same chip type. Driver API surface: `cuCheckpointProcessLock/Checkpoint/Restore/Unlock`.

Two things to keep straight:

- **This path does not DMA like GDS.** Device memory is staged into *host* memory during suspend, then persisted by CRIU. Suspend time is bounded by the resident device-memory image size and host-link bandwidth — profile it with Nsight Systems markers around the lock and checkpoint calls.
- **It is orthogonal to framework checkpoints.** Use it for fault tolerance, preemption, and job migration; it complements, never replaces, DCP / state-dict checkpoints (see the skill's Checkpointing at Scale section).

## Diagnosing a Dataloader-Bound Run

The skill's Known Traps warns that OOM and low utilization get blamed on GPUs when the dataloader is the real cause. This is the method for attributing it.

`next(data_iterator)` measures total GPU idle waiting for the next batch — which bundles background prefetch *and* the host→device copy, not just Python logic. Split them:

1. **Baseline GPU idle.** Time `next(data_iterator)` across normal training. That is the total stall budget.
2. **Isolate Python/loader cost.** Re-run with `num_workers=0` (no prefetch) and time only the iterator pull. This is what the Python loop plus transforms actually cost.
3. **Isolate H2D copy cost.** Wrap `.to("cuda")` / pinned staging in `torch.cuda.Event` timers, or read the "Copy" lanes in an Nsight Systems timeline.
4. **Compare.** Loader-dominant → fix the Python pipeline (more workers, drop per-element logging, simplify or vectorize transforms, move preprocessing to GPU or offline). Copy-dominant → fix the transfer path (pinned memory, more interconnect bandwidth, GDS).
5. **Loader in isolation.** Time 100 batches with all GPU work disabled and compare against target iteration time. Caveat from the book: disabling GPU kernels also removes CPU kernel-launch overhead, so isolated loader throughput reads *lower* than in a real run — useful, but not a clean number.

Interpretation guide from the profiler timeline: GPUs idle *at the start of every iteration* points at data loading; GPUs idle *inside gradient all-reduce* points at communication instead.

## Dataloader Tuning Knobs

| Knob | Effect | Guidance |
|------|--------|----------|
| `num_workers` | Parallel fetch + preprocess processes (separate processes dodge the GIL) | Empirical. Too few → GPU idle; too many → CPU and I/O contention. Target near-100% disk throughput with CPU headroom |
| Worker count vs GPU count | Aggregate ingest scales with cluster size | Scale workers and I/O bandwidth as you add GPUs, or the bottleneck simply migrates into the pipeline. Each rank reads its own shard |
| `pin_memory=True` | Locks host buffers so H2D uses DMA without on-the-fly pinning | Almost always on. Raise `ulimit -l` / container `--ulimit memlock` for large pinned buffers |
| `non_blocking=True` on `.to(device)` | Async H2D overlapping compute | Only truly async when the source is pinned |
| `prefetch_factor` | Batches queued per worker (`num_workers × prefetch_factor` total); default 2 | Raise to 4–8 for bursty I/O or intermittent worker starvation |
| `persistent_workers=True` | Workers survive epoch boundaries | Worth it for short epochs or expensive worker startup (module imports, file opens) |
| `collate_fn` | Batched vectorized transforms instead of per-sample | Collate then transform the whole batch; some transforms are irreducibly per-sample |

The target pipeline shape: while the GPU computes batch N, the CPU has batch N+1 ready in pinned memory and is already working on N+2. Frameworks do this by default with multiple workers — verify it on a timeline rather than assuming it.

Watch for hidden bottlenecks introduced late: debug logging inside `__getitem__`, or an expensive CPU transform that only shows under load. Prefer fast tokenizers with Rust/C++ backends (Hugging Face Tokenizers) over per-line Python loops.

## GPU-Side Decode (NVIDIA DALI)

DALI moves decode and augmentation onto the GPU (or into optimized C++), defined declaratively as a static operator graph (`nvidia.dali.pipeline.Pipeline`, `define_graph()`), with its own prefetch and thread pools. It shines on image and video pipelines where JPEG decode plus crop/resize/normalize dominates CPU time, and can collapse an eight-core-saturated preprocessing stage to a fraction of that.

The trap: placement. Decoding on GPU and handing raw pixels *back* to the CPU for augmentation and collation adds host-device-host round trips that can erase the gain. Fuse GPU-friendly preprocessing into one GPU graph instead — often via TorchVision/TensorRT CUDA ops or custom kernels, which can beat DALI end-to-end. Benchmark CPU-only vs DALI vs fully fused GPU graph on the real workload.

Better still, do the heavy work offline. NeMo Curator (cleansing, dedup, tokenizing, shuffling, packing into large binary files) leaves the online pipeline reading prepared data with at most light last-mile shuffling. You should almost never train from raw text. One further trade worth considering: store N pre-shuffled copies to avoid runtime shuffle cost across N epochs, paying disk for it.

## Monitoring Toolchain

| Tool | What it shows |
|------|---------------|
| `iostat` | Per-device throughput, IOPS, queue behavior over time |
| `iotop` | Which processes are actually issuing the I/O |
| `nvme-cli` | NVMe device health, namespaces, controller state |
| `perf` / eBPF | Syscall and kernel-path overhead in the read path |
| Nsight Systems | I/O wait vs GPU kernel overlap; `--trace=gds` captures cuFile API activity (enable cuFile tracepoints via `/etc/cufile.json`) |
| DCGM | GPU-side I/O statistics, complementing host OS tools |
| Vendor dashboards (`lmt` for Lustre, etc.) | Queues, latencies, read-ahead effects, cache hit ratios, hot storage nodes |

Kernel-mode counters for NVMe peer-to-peer DMA are not exposed in Nsight Systems and may be unavailable on some GDS stacks.

## Continuous Profiling Workflow

The book's general loop, applied to any bottleneck class:

1. **Establish a baseline.** Measure single GPU (samples/sec), then single-node multi-GPU, then multi-node. Data-parallel scaling should approach N×; quantify the shortfall as a scaling efficiency and treat it as the number to explain.
2. **Profile the multi-GPU run.** Nsight Systems on the whole job. Read the GPU utilization timeline: are GPUs stalling, and on what? Check CPU timelines for a lagging main process or synchronization points where everything waits.
3. **Zoom into kernels if needed.** Nsight Compute on the suspect kernel to classify it as network-bandwidth, memory-bandwidth, or compute bound — it will be one of those three.
4. **Identify the cause.** Enumerate hypotheses and validate them one at a time. GPU idle waiting on other GPUs → straggler / data imbalance. CPU bound → dataloader misconfiguration or a CPU aggregation better suited to the GPU. Network bound → RDMA disabled, message sizes too small, insufficient overlap.
5. **Apply fixes, then remeasure.** Change one or two things at a time. Record the good metric values and defend them as you scale.
6. **Automate.** Nightly profiling runs plus a samples/sec dashboard catch regressions and tie them to code changes; hardware and software updates move the optimum over time.

## Canonical Sources

- Chris Fregly, *AI Systems Performance Engineering*, O'Reilly (Nov 2025), Ch. 5 — "GPU-Based Storage I/O Optimizations": https://www.oreilly.com/library/view/ai-systems-performance/9798341627772/
- NVIDIA GPUDirect Storage documentation (cuFile API, `nvidia-fs`, `gdsio`): https://docs.nvidia.com/gpudirect-storage/
- NVIDIA DALI: https://github.com/NVIDIA/DALI
- PyTorch `DataLoader` reference (`num_workers`, `pin_memory`, `prefetch_factor`, `persistent_workers`): https://docs.pytorch.org/docs/stable/data.html
- DeepSeek 3FS (Fire-Flyer File System, random-read-optimized, RDMA-first): https://github.com/deepseek-ai/3FS
