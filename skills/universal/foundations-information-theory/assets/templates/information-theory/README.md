# Information Theory Primitive Playbooks

One file per primitive: definition, traps, a re-derived known answer, and sources. The primitive table, anti-patterns and composition recipes live in [`../../../SKILL.md`](../../../SKILL.md); domain anti-patterns in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md); LLM evaluation and serving rules in [`../../../references/llm-practice.md`](../../../references/llm-practice.md).

| # | File | Failure mode it addresses |
|---|------|--------------------------|
| 1 | [01-shannon-entropy.md](01-shannon-entropy.md) | Unquantified uncertainty; biased plug-in estimates |
| 2 | [02-mutual-information.md](02-mutual-information.md) | Linear-only dependence; biased finite-sample MI |
| 3 | [03-kl-divergence.md](03-kl-divergence.md) | Symmetric-distance misuse; wrong direction; support failures |
| 4 | [04-cross-entropy.md](04-cross-entropy.md) | CE-as-similarity; tokenizer-dependent perplexity |
| 5 | [05-channel-capacity.md](05-channel-capacity.md) | Throughput claims without a channel model |
| 6 | [06-rate-distortion.md](06-rate-distortion.md) | Lossy-rate claims without a named distortion |
| 7 | [07-mdl-principle.md](07-mdl-principle.md) | Model complexity not penalized; arbitrary codes |
| 8 | [08-information-bottleneck.md](08-information-bottleneck.md) | Representation retains task-irrelevant information |
| 9 | [09-fano-inequality.md](09-fano-inequality.md) | Optimistic error floors; misread vacuous bounds |
| 10 | [10-typical-sets-aep.md](10-typical-sets-aep.md) | Asymptotic limits read as finite guarantees |
| 11 | [11-redundancy-compression.md](11-redundancy-compression.md) | Wrong code family; compression read as meaning preservation |

Every number in a playbook is a hypothetical known answer re-derived from its stated inputs, not a benchmark to transfer.
