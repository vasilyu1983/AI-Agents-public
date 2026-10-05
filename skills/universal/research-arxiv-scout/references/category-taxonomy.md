# arXiv Category Taxonomy (AI/Engineering Focus)

Use this to pick categories when a target does not map cleanly in `config.yaml`.

## Tier 1 (primary)

- `cs.AI` Artificial Intelligence: agents, planning, reasoning
- `cs.CL` Computation and Language: LLMs, NLP, prompting
- `cs.LG` Machine Learning: training, architectures, optimization
- `cs.IR` Information Retrieval: retrieval, ranking, RAG
- `cs.SE` Software Engineering: program analysis, testing, code quality

## Tier 2 (common adjacent)

- `cs.CR` Cryptography and Security: robustness, safety, privacy, adversarial work
- `cs.DB` Databases: vector DBs, indexing, query processing
- `cs.DC` Distributed Computing: serving, scaling, distributed training
- `cs.PF` Performance: profiling, latency, throughput
- `cs.NI` Networking/Internet: internet systems, API patterns

## Tier 3 (special cases)

- `cs.MA` Multiagent Systems: coordination and communication
- `stat.ML` ML (Statistics): evaluation, uncertainty, statistical testing

## Example query patterns

Agents:

```text
cat:cs.AI AND (agents OR planning OR reasoning OR "tool use")
```

Prompting:

```text
cat:cs.CL AND (prompt OR "in-context learning" OR "chain of thought")
```

RAG:

```text
cat:cs.IR AND ("retrieval augmented" OR RAG OR reranking OR embeddings)
```

Software testing:

```text
cat:cs.SE AND (testing OR "test generation" OR "fuzzing")
```

Security:

```text
cat:cs.CR AND (LLM OR "prompt injection" OR jailbreak OR adversarial)
```
