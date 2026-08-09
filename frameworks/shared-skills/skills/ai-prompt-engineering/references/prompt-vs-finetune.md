# Prompt vs RAG vs Fine-tune vs Distill

Decision reference for choosing the right adaptation strategy. This file covers escalation criteria only — for RAG depth see [ai-rag](../../ai-rag/SKILL.md); for model strategy see [ai-llm](../../ai-llm/SKILL.md).

## Escalation Ladder

| Stage | Use when | Escalate when |
|-------|----------|---------------|
| **Prompt engineering** | Task is new or low-volume; behavior can be described in text | Output quality plateaus despite good examples and schema; task requires knowledge the model lacks |
| **RAG** | Model lacks domain knowledge or recency; facts change frequently; sourcing and citations matter | Retrieval quality plateaued; latency or cost too high; task is format/style, not knowledge |
| **Fine-tuning** | High volume; stable task; consistent I/O format; prompt is too long or slow to iterate | Quality still insufficient; task requires distilled reasoning, not just format adaptation |
| **Distillation** | Need smaller/cheaper model at scale; teacher model output quality is sufficient | Teacher output is not good enough to train from |

## Decision Rules

1. **Start with prompting.** Every other stage costs more to set up and maintain.
2. **Add RAG before fine-tuning** when the gap is knowledge, not behavior.
3. **Fine-tune for format and style at scale**, not to inject facts — facts drift; fine-tuned weights do not update.
4. **Distill to compress cost**, not to improve quality — the distilled model will not outperform the teacher.

## Warning Signs

- Prompting: eval score does not improve after 5+ prompt iterations → move to RAG or fine-tune.
- RAG: retrieval-adjusted eval is still below target → the gap is behavioral, not knowledge.
- Fine-tuning: no labeled data available → do not fine-tune; use few-shot prompting or RAG.
- Distillation: teacher model is still being iterated → wait until teacher behavior is stable.

## Cross-links

- Automatic prompt optimization (DSPy/MIPROv2): see [references/additional-patterns.md](additional-patterns.md) §12.
- RAG architecture and retrieval quality: [ai-rag](../../ai-rag/SKILL.md).
- Model selection and lifecycle: [ai-llm](../../ai-llm/SKILL.md).
- Fine-tuning operations: [ai-mlops](../../ai-mlops/SKILL.md).
