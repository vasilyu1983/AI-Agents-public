# Failure Budget and Checkpoint Interval

Distilled from Vijay Janapa Reddi, *Machine Learning Systems* (MLSysBook, open textbook, Oct 2025), Chapter 16 "Robust AI", §16.4 Hardware Faults (book pp. 1400–1404). Use this when you need to **choose** a checkpoint interval rather than implement one.

The skill's [Checkpointing at Scale (DCP)](../SKILL.md#checkpointing-at-scale-dcp) section covers the *mechanics* — sharded save, `dcp.async_save`, spot-preemption discipline. This file covers the *cadence*: how often, derived from the cluster's failure rate rather than picked by feel.

## Table of Contents

- [Reading Note: What Is Durable Here and What Is Not](#reading-note-what-is-durable-here-and-what-is-not)
- [Fault Taxonomy](#fault-taxonomy)
- [Cluster-Level MTBF: The Compounding Arithmetic](#cluster-level-mtbf-the-compounding-arithmetic)
- [Deriving the Checkpoint Interval](#deriving-the-checkpoint-interval)
- [Fault-Tolerance Overhead (Textbook-Reported)](#fault-tolerance-overhead-textbook-reported)
- [ECC and Memory Bandwidth](#ecc-and-memory-bandwidth)
- [Silent Data Corruption in Large Checkpoints](#silent-data-corruption-in-large-checkpoints)
- [Applying This to a Real Run](#applying-this-to-a-real-run)
- [Canonical Sources](#canonical-sources)

## Reading Note: What Is Durable Here and What Is Not

Separate these two before using anything below.

**Durable — the method.** Derive the checkpoint interval from *cluster-level* MTBF, not per-device MTBF; weigh checkpoint cost against expected lost work. That reasoning holds regardless of which numbers you plug in, and it is the reason this file exists.

**Not durable — the specific figures.** The textbook gives MTBF ranges ("Cloud AI accelerators (Tesla V100, A100): MTBF of 50,000-100,000 hours"), a fault-tolerance overhead table (Table 16.1), and memory-bandwidth overheads (Table 16.2) **with no measurement citation attached to any of them**. Treat every number below as textbook-illustrative — useful for showing the shape of the tradeoff, not as a measured fact about your hardware. Verify against vendor specs, your own cluster's failure log, or a published reliability study before any figure lands in a capacity plan or a budget.

Where the textbook *does* cite a source, this file names it (Baumann 2005, Reagen et al. 2018). Where it does not, this file says so.

## Fault Taxonomy

Reddi Ch. 16 splits hardware faults into three classes. The distinction matters because each demands a different mitigation, and only one of them is what checkpointing actually protects against.

| Class | Cause | ML training impact | Primary mitigation |
|-------|-------|-------------------|-------------------|
| **Transient** | External, non-recurring — cosmic rays, EMI, voltage fluctuation. No permanent hardware damage. | "can corrupt gradient updates during training or alter model weights during inference, leading to temporary but potentially significant performance degradation" | ECC, detection + retry. Checkpoints do not help if the corruption goes undetected. |
| **Permanent** | Irreversible physical damage — stuck-at faults, device failures, wear-out. Requires hardware replacement. | "particularly problematic for long-running ML training jobs, where hardware failure can result in days or weeks of lost computation and require complete job restart from the most recent checkpoint" | Checkpoint + restart. This is the class the interval arithmetic below targets. |
| **Intermittent** | Unstable conditions — loose connections, aging components. Appears and disappears sporadically. | "can cause non-deterministic behavior in ML systems, leading to inconsistent results that compromise model validation and reproducibility" | Hardest to diagnose; node quarantine / drain on repeated soft failure. |

Practical consequence: a run that fails loudly (NCCL timeout, node eviction, process crash) is the permanent/intermittent case and checkpoint cadence bounds the loss. A run that *does not* fail but produces a bad loss curve may be the transient case, where a checkpoint restore just replays the same corruption — see [Silent Data Corruption](#silent-data-corruption-in-large-checkpoints).

## Cluster-Level MTBF: The Compounding Arithmetic

The load-bearing insight. Verbatim from Reddi Ch. 16, p. 1402:

> "A cluster of 1,000 accelerators with individual MTBF of 50,000 hours experiences an expected failure every 50 hours, necessitating robust checkpointing and recovery mechanisms."

The arithmetic is just `cluster_MTBF ≈ device_MTBF / N` under the textbook's stated assumption of independent, exponentially-distributed failures during the useful-life period (the MTBF sidebar on p. 1402 names that assumption explicitly, attributing the formalization to MIL-HDBK-217, 1965).

```text
cluster_MTBF_hours ≈ device_MTBF_hours / num_devices

  50,000 / 1,000 =  50 h        # the textbook's worked example
  50,000 /   256 = 195 h
  50,000 /     8 = 6,250 h      # a single node: failure is not your binding constraint
```

Two things this model does *not* capture, and you should not pretend otherwise:

- **Correlated failure.** A rack power event, a bad switch, or a shared cooling fault takes many devices at once. Independence is the assumption that makes the division valid, and it is the assumption most likely to be wrong in a real data center.
- **Non-accelerator failure modes.** Host memory, NICs, the storage layer, and the scheduler all fail too. Device MTBF is a floor on the job's failure rate, not the whole of it. Spot/interruptible preemption is a separate and usually *far more frequent* interruption source than hardware failure — see [Rented GPU Cost Guide](rented-gpu-cost.md).

The device-level MTBF ranges the textbook offers, all uncited and stated for whole deployment classes rather than specific parts: cloud accelerators (it names Tesla V100 and A100) at 50,000–100,000 hours under controlled data-center conditions; edge processors (Jetson, Movidius) at 20,000–40,000 hours in uncontrolled environments; mobile AI chips at 30,000–60,000 hours under thermal and power constraints. Use the shape — controlled environments roughly 2× the field ones — not the digits.

## Deriving the Checkpoint Interval

The textbook's rule, verbatim from the MTBF sidebar (p. 1402):

> "For AI systems, MTBF analysis guides checkpoint frequency - a system with 50,000-hour MTBF should checkpoint every 1-2 hours to minimize recovery overhead while maintaining <1% performance impact from fault tolerance."

Read that carefully: it is stated against the *system's* 50,000-hour MTBF, and the 1–2 hour answer only makes sense once that MTBF has been divided down to the cluster level (50,000 / 1,000 = 50 h, checkpoint at roughly 2–4% of the failure interval). Applying "50,000-hour MTBF → checkpoint every 1–2 hours" to a single 8-GPU node would be a serious over-checkpoint. The method is what transfers; the numbers are one point on the curve.

**The tradeoff being balanced.** Every checkpoint costs write time; every failure costs the work since the last checkpoint. Expected waste per unit of training time is roughly:

```text
waste ≈ (checkpoint_cost / interval)  +  (interval / 2) / cluster_MTBF
        └── overhead you pay always ──┘  └── expected work lost per failure ──┘
```

Minimizing gives the classic square-root form (Young/Daly, standard HPC result — *not* from Reddi, which states no formula):

```text
optimal_interval ≈ sqrt(2 × checkpoint_cost × cluster_MTBF)
```

Worked against the textbook's own example — 1,000 accelerators, cluster MTBF 50 h — with a checkpoint that costs 1 minute of stalled training:

```text
sqrt(2 × (1/60) h × 50 h) ≈ 1.3 h
```

which lands inside the textbook's stated 1–2 hour band. That agreement is a sanity check on the reasoning, not independent confirmation of the numbers: both rest on the same uncited 50,000-hour figure.

**What actually moves your answer:**

- **`checkpoint_cost` is the lever you control.** `dcp.async_save` overlaps the write with training, driving the *stalled* portion toward the tens-of-seconds range and pushing the optimal interval down — you can afford to checkpoint far more often. A synchronous full-`state_dict` save on a large model can cost many minutes, which both raises the interval and wastes more on every failure. This is the concrete reason the SKILL.md guidance to use DCP async save is not just hygiene.
- **Spot instances change the regime entirely.** Preemption rates are measured in hours, not the 50-hour cluster MTBF above, so the interruption interval — not hardware MTBF — is the number to divide by. Checkpoint on step count tuned to that.
- **Do not let the interval exceed what you can afford to lose.** If eight hours of a rented H100 cluster is real money, that ceiling binds before any MTBF arithmetic does.

## Fault-Tolerance Overhead (Textbook-Reported)

Reddi Table 16.1 (p. 1402), "Fault Tolerance Overhead Analysis". **The table carries no citation in the textbook** — no measurement study, no vendor spec, no benchmark is named for any cell. Reproduced here for the relative ordering it shows, not as measured fact. Verify against vendor specs before using any figure in a decision.

| Protection Mechanism | Performance Overhead | Energy Overhead | Area Overhead |
|---------------------|---------------------|-----------------|---------------|
| Single-bit ECC | 2-5% | 3-7% | 12-15% |
| Double-bit ECC | 5-12% | 8-15% | 25-30% |
| Triple Modular Redundancy | 200-300% | 200-300% | 200-300% |
| Checkpoint/Restart | 10-25% | 15-30% | 5-10% |

The ordering is the usable part and it is uncontroversial: ECC is cheap enough to leave on unconditionally; TMR triples your cost and belongs in avionics and space, not a training cluster; checkpoint/restart sits in between and is the only row you actively tune. Note that the 10-25% checkpoint/restart performance overhead is precisely the quantity that async, sharded checkpointing is designed to shrink — treat that row as an untuned baseline, not a floor.

## ECC and Memory Bandwidth

Verbatim from Reddi p. 1402:

> "ECC memory reduces effective bandwidth by 12.5% due to additional storage requirements (8 ECC bits per 64 data bits)."

The 12.5% here is arithmetic (8/64), not a measurement, and that part is sound. What is *not* established by the textbook is that the storage ratio translates one-to-one into delivered bandwidth loss on real memory systems — that depends on controller design and access patterns, and no measurement is cited. The book adds that memory scrubbing consumes "additional 5-15% of available bandwidth depending on scrubbing frequency and memory configuration", also uncited.

Its worked example, same page: a model requiring 900 GB/s with ECC protection "effectively receives only 787 GB/s, extending training time by approximately 14%." That extension figure assumes the workload is purely memory-bandwidth-bound — which large transformer training often is *in parts*, not throughout. Do not apply it as a flat 14% tax on a training run.

Why this matters for distributed training specifically: it is not a knob you get to turn. Data-center accelerators ship with ECC enabled and you should leave it that way — the alternative is silent weight corruption. The practical use of this number is honesty in throughput accounting: when your measured HBM bandwidth falls short of the datasheet peak, ECC and scrubbing are part of why, and chasing that gap as if it were a tuning bug wastes time.

## Silent Data Corruption in Large Checkpoints

Verified present in the source (p. 1401 sidebar, note 14). Reddi cites Baumann 2005 for the underlying DRAM error rate — approximately 1 error per 10^17 bits accessed, roughly once per gigabit per month at sea level — and then extrapolates:

> "For AI systems processing large datasets, a 1 TB model checkpoint experiences an expected 80 bit flips during a single read operation, making error detection essential for reliable ML training."

**Hedge this hard.** The 10^17 base rate is cited; the 80-bit-flips extrapolation is the textbook's own and carries no separate citation. It also reads as a raw-DRAM figure with no ECC correction applied — on ECC memory, single-bit errors in that stream are corrected, which is the entire point of the protection the same chapter recommends. Take the direction (checkpoint reads at terabyte scale are large enough that per-bit error rates stop being negligible), not the magnitude.

The chapter also reports, citing Reagen et al. 2018, that "a single, targeted bit-flip in a key layer can drop ImageNet accuracy from 76% to less than 10%" — note *targeted*, an adversarially-chosen worst case, not what a random flip does.

Operationally, the defensible takeaways do not depend on the disputed number:

- **Checksum your checkpoints.** Write a hash alongside each checkpoint and verify on restore. Cheap relative to the write, and it converts a silent corruption into a loud failure.
- **Keep more than one checkpoint.** If restore-time verification fails, you need somewhere to fall back to. Retaining the last N is the standard answer.
- **A loss curve that goes bad without a crash is a corruption candidate.** Restoring from the most recent checkpoint may replay it. Fall back further and compare.

## Applying This to a Real Run

1. **Get a cluster-level failure interval, not a device one.** Divide device MTBF by device count for a first cut; replace it with your own observed interval (job failures per GPU-hour from the scheduler log) as soon as you have one. Observed beats textbook, always.
2. **On spot/interruptible, use the preemption interval instead.** It dominates hardware MTBF by orders of magnitude. Hardware MTBF is the wrong input there.
3. **Measure `checkpoint_cost` as the *stalled* time, not the write time.** With `dcp.async_save` these differ substantially, and the stalled time is what enters the arithmetic.
4. **Compute an interval, then cap it by loss tolerance.** `sqrt(2 × checkpoint_cost × cluster_MTBF)` (the cluster failure interval from step 1, or the preemption interval from step 2; e.g. sqrt(2 × (1/60) h × 50 h) ≈ 1.3 h), then cap it at the most training time you are willing to lose.
5. **Convert to steps and verify restore.** Interval in hours becomes a step count via measured step time. Test the restore path before the long run — an untested checkpoint is not a checkpoint.
6. **Checksum on write, verify on read.**

## Canonical Sources

- Vijay Janapa Reddi, *Machine Learning Systems* (MLSysBook, open textbook, Oct 2025), Ch. 16 "Robust AI", §16.4 Hardware Faults, book pp. 1400–1404 — fault taxonomy, MTBF ranges, cluster-MTBF compounding, Table 16.1 fault-tolerance overhead, Table 16.2 memory-bandwidth protection: https://mlsysbook.ai/
- R. Baumann, "Radiation-induced soft errors in advanced semiconductor technologies" (2005) — cited by Reddi as the source for the DRAM soft-error rate and the 7 nm vs 65 nm comparison. Read it directly before quoting either.
- B. Reagen et al. (2018) — cited by Reddi for the targeted-bit-flip accuracy result. Read directly before quoting.
- J. W. Young (1974) / J. T. Daly (2006), optimal checkpoint interval — the `sqrt(2 × cost × MTBF)` result used above. **Not from Reddi**; standard HPC literature.
