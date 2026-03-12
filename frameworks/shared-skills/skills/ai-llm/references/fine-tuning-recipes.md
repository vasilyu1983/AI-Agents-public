# Fine-Tuning Recipes (SFT, Instruction Tuning, PEFT/LoRA)

Operational workflows for running safe, reproducible LLM fine-tuning with modern parameter-efficient methods.

---

## Modern Best Practices (2024-2025)

**PEFT/LoRA is now standard**:
- Minimizes trainable parameters while improving performance
- Significantly reduced computational requirements
- LoRA adapters can be saved separately for efficient deployment

**Key Insight**: Combining techniques (fine-tuned model + prompt engineering + RAG) yields best results

**Regular monitoring**: Evaluate on validation data to detect overfitting/underfitting early

---

## Strategy Selection: When to Fine-Tune

Use this decision matrix to choose between prompting, fine-tuning, and RAG:

| Use Case | Best Approach | Rationale (Modern Research) |
|----------|---------------|---------------------------|
| MVP / Prototype | **Prompt Engineering** | Simplicity, speed, agility - quick deployment with minimal setup |
| Internal tools | **Prompt Engineering** | Fast iteration, low overhead |
| Production with sufficient data | **Fine-Tuning (PEFT/LoRA)** | Highest performance when data available |
| Cold-start (insufficient data) | **Few-shot prompting** | No persona needed for best results |
| Dynamic knowledge | **RAG** | Current information, evolving content |
| Code review automation | **Fine-Tuning** | Research shows fine-tuning achieves highest performance |
| Clinical classification | **Prompting with reasoning** | Clear, concise prompts with reasoning steps |
| Best results | **Combined: Fine-tuning + Prompting + RAG** | Hybrid approaches yield optimal outcomes |

**Trade-offs**:
- **Prompt engineering**: Fast, flexible, no training required, but may have lower accuracy
- **Fine-tuning**: Highest performance, domain specialization, but requires data and compute
- **RAG**: Access to current knowledge, but adds latency and complexity

---

## Recipe 1: Supervised Fine-Tuning (SFT) with PEFT

**Use when**: Training a model on instruction datasets with parameter efficiency

### Steps (Modern PEFT-first approach)

1. **Define model choice**
   - Model size and context window requirements
   - Hardware budget (GPU VRAM)
   - **PEFT strategy** (Modern Standard):
     - LoRA (Low-Rank Adaptation) - efficient fine-tuning
     - Updates only minor fraction of model parameters
     - Significantly reduced computational requirements
     - Choose between: training from scratch vs modifying existing model (adapting often more efficient)

2. **Prepare dataset**
   - Clean, dedupe, structure
   - Remove harmful or contradictory examples
   - Validate consistency in structure
   - Each example must represent *ideal* model behavior
   - Balance distribution of task types

3. **Training configuration (PEFT-optimized)**
   - Learning rate: 1e-5 – 2e-5 (typical for full fine-tuning)
   - Learning rate: 2e-4 (for LoRA)
   - Batch size: match VRAM constraints
   - Max steps vs epochs
   - **LoRA parameters**:
     - Rank: 8–32
     - Alpha: 16–32
     - Target modules: attention layers
   - Seed fixed for reproducibility
   - Use 4-bit quantization (QLoRA) for VRAM savings

4. **Checkpointing & evaluation** (Modern critical)
   - Periodic eval on held-out set
   - Monitor for overfitting/underfitting
   - Early stopping logic
   - Regular validation data evaluation
   - Save best checkpoint by validation loss

5. **Packaging**
   - Save tokenizer + model config
   - Save PEFT adapters separately for efficient deployment
   - Export `training_log.json` with metrics
   - Document hyperparameters and data provenance

### Checklist: SFT complete

- [ ] Dataset validated and deduped
- [ ] PEFT/LoRA strategy selected and configured
- [ ] Hyperparameters recorded (LR, rank, alpha, batch size)
- [ ] Model evaluated against baseline
- [ ] Regular validation checks for overfitting/underfitting
- [ ] Best checkpoint chosen & exported
- [ ] PEFT adapters saved separately for efficient deployment
- [ ] Training logs and metrics documented

---

## Recipe 2: Instruction Tuning

**Use when**: Building general-purpose assistant behavior

### Additional requirements beyond SFT

- Diverse task instructions across domains
- Balance categories (classification, summarization, transformation, Q&A)
- Avoid conflicting examples
- Include refusal examples for unsafe tasks
- Test multi-turn conversations if chat format
- Validate instruction-following on edge cases

### Dataset composition

- 30-40% Knowledge tasks (Q&A, factual)
- 20-30% Reasoning tasks (math, logic)
- 20-30% Creative tasks (writing, brainstorming)
- 10-20% Safety/refusal examples

### Checklist: Instruction tuning ready

- [ ] Task diversity verified across categories
- [ ] Refusal examples included (unsafe, out-of-scope)
- [ ] Multi-turn conversation tested
- [ ] Instruction-following validated on edge cases
- [ ] Dataset balanced across task types

---

## Recipe 3: LoRA / QLoRA (Parameter-Efficient Fine-Tuning)

**Use when**: Limited compute resources or need for rapid iteration

### LoRA Configuration

1. **Freeze base model** (all parameters)
2. **Attach low-rank adapters** to attention layers
3. **Train with**:
   - Learning rate: 2e-4 (higher than full fine-tuning)
   - Rank (r): 8–32 (balance between capacity and efficiency)
   - Alpha: 16–32 (scaling factor, typically 2x rank)
   - Target modules: query, key, value projections
4. **Use 4-bit quantization** (QLoRA) for VRAM savings
5. **Merge adapters** if needed for inference (or keep separate)

### Parameter selection guide

| Task Complexity | Rank | Alpha | Notes |
|----------------|------|-------|-------|
| Simple tasks | 8 | 16 | Classification, extraction |
| Medium tasks | 16 | 32 | General instruction following |
| Complex tasks | 32 | 64 | Reasoning, code generation |

### Checklist: LoRA complete

- [ ] Rank, alpha, target modules recorded
- [ ] BF16/FP16 stability checked
- [ ] Merged model validated (if merging)
- [ ] Adapter files saved separately
- [ ] Inference tested with adapters

---

## Recipe 4: Safety Requirements for Fine-Tuning

### Avoid in training data

- Private data (PII, credentials, internal info)
- Toxic/unsafe content
- Contradictory behaviors (conflicting instructions)
- "Do anything now" jailbreak patterns
- Malicious code or exploits

### Add to training data

- Refusal examples for unsafe requests
- Safety-guided templates
- Negative examples (what not to do)
- Boundary cases for allowed vs disallowed content

### Safety validation

- Test with adversarial prompts
- Verify refusal behavior on unsafe requests
- Check for data leakage (PII, training data)
- Validate policy compliance

### Checklist: Safety verified

- [ ] No PII or sensitive data in dataset
- [ ] Refusal examples included
- [ ] Adversarial testing completed
- [ ] No safety regressions vs base model
- [ ] Policy compliance validated

---

## Recipe 5: Context Window & Build Considerations

**When building/choosing models or heavy adaptation**

### Tokenizer/Encoding

- Decide BPE vs unigram for tokenization
- Cover domain-specific tokens (code, medical, legal)
- Avoid excessive splits on code/PII markers
- Validate tokenizer on domain corpus sample

### Scaling Laws

- Set data/parameter/compute budget
- Prefer more tokens over parameters if data-rich
- Follow Chinchilla scaling: 20 tokens per parameter

### Context Optimizations

- FlashAttention-2 for memory efficiency
- Paged KV cache for longer contexts
- Positional embeddings (RoPE/YaRN)
- Sliding-window attention for very long docs

### Training Stability

- Warmup schedule + cosine decay
- Gradient clipping (1.0 typical)
- Optimizer: AdamW with decoupled weight decay
- Monitor loss spikes and gradient norms

### Evaluation While Training

- Perplexity on validation set
- Task probes (accuracy on key tasks)
- Long-context stress tests
- Stop if loss flattens but eval regresses

### Checklist: Architecture ready

- [ ] Tokenizer built/validated on domain corpus
- [ ] Compute/data budget documented with scaling target
- [ ] Attention + KV strategy chosen for target context length
- [ ] Optimizer schedule + clipping configured
- [ ] Long-context eval included in dev loop

---

## Recipe 6: Data & Feedback Loops (Production)

**Use when**: You have production users/traffic and need continuous improvement

### Signal Capture

- Log prompts + outputs + ratings/edits with PII scrubbing
- Store failure exemplars (hallucinations, refusals, toxicity)
- Track user satisfaction metrics
- Capture edge cases and errors

### Labeling Loop

- Triage failures to human review queue
- Turn critiques into supervised pairs (input → ideal answer)
- Build preference data for DPO/ORPO (pairwise comparisons)
- Validate labels for consistency

### Contamination Control

- Keep eval/test IDs separate from training
- Block leakage of eval data into training set
- Hash samples to detect re-ingestion
- Version datasets with lineage tracking

### Dataset Refresh Cadence

- Nightly/weekly slices from production logs
- Auto-balance domains and task types
- Retire stale data (>6 months old)
- Track lineage (source → cleaning → split)

### Online Evaluation

- Shadow models/prompts in production
- Tie quality metrics to product KPIs (solve rate, deflection, cost, latency)
- A/B test new versions before full rollout

### Checklist: Feedback loop live

- [ ] Logging with privacy/PII scrubbing enabled
- [ ] Human-in-loop queue + labeling rubric active
- [ ] Eval sets protected from contamination
- [ ] Refresh cadence + lineage metadata stored
- [ ] Online/shadow eval tied to KPIs

---

## Recipe 7: Final Validation Checklist

Before deploying any fine-tuned model:

- [ ] Evaluation suite passed (accuracy ≥ threshold)
- [ ] JSON output stability verified (schema compliance)
- [ ] No safety regressions observed vs base model
- [ ] Refusal behavior validated on unsafe requests
- [ ] Performance benchmarks met (latency, throughput)
- [ ] Documentation completed (dataset, hyperparams, metrics)
- [ ] Model artifacts packaged (tokenizer, config, adapters)
- [ ] Rollback plan ready
- [ ] Monitoring/alerting configured  
