# ML Diagram Catalog (Mermaid)

Reusable Mermaid diagrams for classical ML algorithms and neural network architectures. Drop into READMEs, docs, PR descriptions, notebooks, or agent outputs.

## Table of Contents

- [When to Use](#when-to-use)
- [Authoring Conventions](#authoring-conventions)
- [Classical ML](#classical-ml)
- [Neural Network Architectures](#neural-network-architectures)
  - [Feedforward (MLP)](#feedforward-mlp)
  - [Recurrent Neural Network](#recurrent-neural-network-unrolled)
  - [Convolutional Neural Network](#convolutional-neural-network-image-classifier)
  - [Transformer (original encoder)](#transformer-encoder-block--full-stack)
  - [Modern LLM Decoder Block](#modern-llm-decoder-block-production-grade)
  - [Mixture of Experts FFN](#mixture-of-experts-moe-ffn-sublayer)
  - [State Space Model (Mamba)](#state-space-model-block-mamba-style)
  - [Vision Transformer (ViT)](#vision-transformer-vit)
  - [Diffusion Transformer (DiT)](#diffusion-transformer-dit--imagevideo-generation)
  - [Multimodal VLM (LLaVA-style)](#multimodal-vision-language-model-llava-style)
  - [Reasoning model training loop](#reasoning-model-training-loop-rl-with-cot)
- [Variants Worth Adding](#variants-worth-adding)
- [Anti-Patterns](#anti-patterns)

## When to Use

- Documenting an ML pipeline in markdown-rendered surfaces (GitHub, Notion, Obsidian, MkDocs)
- Writing PR descriptions for model changes that need a quick "before/after"
- Teaching, onboarding, or explaining a model family without slide tooling

Skip for: mathematical derivations (use LaTeX), trained-model artifacts (use SHAP / netron / TensorBoard), system-level infra diagrams (different skill).

## Authoring Conventions

- **`flowchart LR/TB/TD`** for pipelines and sequential ops.
- **`subgraph`** to encapsulate repeated blocks (transformer encoder, RNN cell).
- **Edge labels** carry *data shape*; **node labels** carry *operation*.
- **`(())` double-circle** for residual sums / merges.
- **`{}` diamond** for branching decisions (decision trees, convergence checks).
- Quote labels (`"..."`) when they contain `()`, `:`, `/`, or commas.

---

## Classical ML

### K-Means Clustering

```mermaid
flowchart TD
    A[Input: unlabeled data X ∈ ℝⁿˣᵈ] --> B[Choose k clusters]
    B --> C[Initialize k centroids<br/>random or k-means++]
    C --> D[Assign each point to<br/>nearest centroid<br/>argmin ‖xᵢ − μⱼ‖²]
    D --> E[Recompute centroids<br/>μⱼ = mean of assigned points]
    E --> F{Centroids<br/>moved?}
    F -- yes --> D
    F -- no --> G[Output: cluster labels<br/>+ final centroids]
```

### Logistic Regression

```mermaid
flowchart LR
    X[Features x] --> L[Linear: z = wᵀx + b]
    L --> S[Sigmoid: σz = 1 / 1+e⁻ᶻ]
    S --> P[Probability ŷ ∈ 0,1]
    P --> C[Binary cross-entropy loss<br/>L = −y log ŷ − 1−y log 1−ŷ]
    C --> G[Gradient ∂L/∂w, ∂L/∂b]
    G --> U[SGD update<br/>w ← w − η ∇w]
    U -. next batch .-> L
```

### Decision Tree (classification)

```mermaid
flowchart TD
    R[Root: all samples] --> Q1{feature_3 ≤ 0.42?}
    Q1 -- yes --> Q2{feature_7 ≤ 1.10?}
    Q1 -- no --> Q3{feature_1 ≤ −0.30?}
    Q2 -- yes --> L1[Leaf: class A<br/>n=124, gini=0.08]
    Q2 -- no --> L2[Leaf: class B<br/>n=58, gini=0.11]
    Q3 -- yes --> L3[Leaf: class B<br/>n=77, gini=0.05]
    Q3 -- no --> Q4{feature_9 ≤ 2.5?}
    Q4 -- yes --> L4[Leaf: class C<br/>n=43, gini=0.14]
    Q4 -- no --> L5[Leaf: class A<br/>n=91, gini=0.06]
```

### Collaborative Filtering (matrix factorization)

```mermaid
flowchart LR
    subgraph Input
        R[User–Item matrix R<br/>m × n, sparse ratings]
    end
    R --> F[Factorize<br/>R ≈ U · Vᵀ]
    F --> U[User embeddings U<br/>m × k]
    F --> V[Item embeddings V<br/>n × k]
    U --> P[Predict r̂_ui = uᵤᵀ vᵢ]
    V --> P
    P --> Loss[Loss = Σ_obs r_ui − r̂_ui² + λ‖U‖²+‖V‖²]
    Loss --> Opt[SGD / ALS update]
    Opt -. iterate .-> F
    P --> Rec[Top-N recommendations<br/>for user u]
```

---

## Neural Network Architectures

### Feedforward (MLP)

```mermaid
flowchart LR
    X["Input x ∈ ℝᵈ"] --> H1["Dense 128 + ReLU"]
    H1 --> H2["Dense 64 + ReLU"]
    H2 --> H3["Dense 32 + ReLU"]
    H3 --> O["Dense C + Softmax"]
    O --> Y["Class probabilities"]
```

### Recurrent Neural Network (unrolled)

```mermaid
flowchart LR
    X1[x₁] --> C1[RNN cell]
    H0[h₀] --> C1
    C1 --> H1[h₁]
    C1 --> Y1[y₁]

    X2[x₂] --> C2[RNN cell]
    H1 --> C2
    C2 --> H2[h₂]
    C2 --> Y2[y₂]

    X3[x₃] --> C3[RNN cell]
    H2 --> C3
    C3 --> H3[h₃]
    C3 --> Y3[y₃]

    XT[xₜ] --> CT[RNN cell]
    H3 -. ... .-> CT
    CT --> HT[hₜ]
    CT --> YT[yₜ]
```

Every cell shares parameters `Wₕ, Wₓ, b` — the unroll is conceptual, not architectural. LSTM/GRU swap the inner cell for a gated variant but keep this skeleton.

### Convolutional Neural Network (image classifier)

```mermaid
flowchart LR
    I["Image B,32,32,3"] --> C1["Conv 3x3, 32 filters + ReLU"]
    C1 --> P1["MaxPool 2x2"]
    P1 --> C2["Conv 3x3, 64 filters + ReLU"]
    C2 --> P2["MaxPool 2x2"]
    P2 --> C3["Conv 3x3, 128 filters + ReLU"]
    C3 --> GAP["Global Avg Pool"]
    GAP --> FC["Dense 256 + ReLU + Dropout"]
    FC --> OUT["Dense 10 + Softmax"]
```

### Transformer (encoder block + full stack)

```mermaid
flowchart TB
    subgraph Block["Transformer encoder block"]
        direction TB
        IN[Input embeddings] --> MHA[Multi-Head Self-Attention<br/>Q,K,V projections]
        IN --> R1((+))
        MHA --> R1
        R1 --> N1[LayerNorm]
        N1 --> FFN[FeedForward<br/>Linear → GELU → Linear]
        N1 --> R2((+))
        FFN --> R2
        R2 --> N2[LayerNorm]
        N2 --> OUT[Block output]
    end

    TOK[Token IDs] --> EMB[Token embedding]
    POS[Positions] --> PE[Positional encoding]
    EMB --> SUM((+))
    PE --> SUM
    SUM --> B1[Encoder block × 1]
    B1 --> B2[Encoder block × 2]
    B2 --> BN[... × N]
    BN --> HEAD[Task head<br/>classification / LM / etc.]
```

Notes:
- `(+)` nodes are **residual connections** — without them, deep transformers do not train.
- This is the **post-norm** layout from the original paper. Modern LLMs (GPT, LLaMA) use **pre-norm** (LayerNorm *before* the sublayer, then residual sum) for stability at depth.
- Decoder blocks add (1) **masked** self-attention to prevent peeking at future tokens, and (2) a **cross-attention** layer that consumes encoder output.

### Modern LLM Decoder Block (production-grade)

What frontier-tier decoder-only LLMs actually deploy. Differences from the original block above are highlighted in the notes.

```mermaid
flowchart TB
    subgraph Block["Modern decoder block (pre-norm)"]
        direction TB
        IN[Hidden state h] --> N1[RMSNorm]
        N1 --> ATTN[Grouped-Query Attention<br/>Q heads, KV head-groups<br/>+ RoPE on Q,K<br/>+ KV cache append<br/>+ FlashAttention kernel]
        IN --> R1((+))
        ATTN --> R1
        R1 --> N2[RMSNorm]
        N2 --> FFN[SwiGLU FFN<br/>up + gate + down<br/>or MoE router → top-k experts]
        R1 --> R2((+))
        FFN --> R2
        R2 --> OUT[Hidden state h']
    end

    TOK[Token IDs] --> EMB[Token embedding]
    EMB --> B1[Decoder block × 1]
    B1 --> B2[Decoder block × 2]
    B2 --> BN[... × N]
    BN --> FN[Final RMSNorm]
    FN --> LH[LM head<br/>tied to embedding]
    LH --> LOGITS[Next-token logits]
```

What changed vs the original block:

| Original | Modern production | Why |
|---|---|---|
| LayerNorm | **RMSNorm** | Cheaper, equally stable |
| Post-norm | **Pre-norm** | Trains deeper without divergence |
| Additive positional encoding | **RoPE** applied inside attention to Q,K | Extrapolates to longer context; no separate position embedding to learn |
| Multi-Head Attention | **GQA** (or MQA) | Cuts KV-cache memory by `n_heads / n_kv_groups`× — decisive at long context |
| Plain attention | **+ KV cache + FlashAttention** | KV cache reuses past K,V across decode steps; FlashAttention fuses the softmax to avoid materializing the attention matrix |
| GELU FFN | **SwiGLU** (gated) | Better quality at same parameter count |
| Dense FFN every layer | **MoE router → top-k experts** (frontier-tier) | Decouples capacity from FLOPs per token |
| Encoder + decoder | **Decoder-only** | Simpler; works for both generation and embedding tasks |

### Mixture of Experts (MoE) FFN sublayer

Replaces the dense FFN inside each decoder block in MoE-tier models.

```mermaid
flowchart LR
    H[Token hidden state] --> R[Router<br/>linear → softmax over N experts]
    R --> TK[Top-k selection<br/>typically k=2 of N=8..256]
    TK --> E1[Expert 1<br/>SwiGLU FFN]
    TK --> E2[Expert 2<br/>SwiGLU FFN]
    TK -. inactive .-> EN[Expert N<br/>SwiGLU FFN]
    E1 --> W[Weighted sum<br/>by router probabilities]
    E2 --> W
    W --> OUT[FFN output]
    R --> AUX[Aux load-balancing loss<br/>during training only]
```

Notes:
- Only **k of N** experts run per token — that's the whole point. Total parameter count is large; per-token FLOPs are small.
- The auxiliary loss prevents the router from collapsing to one expert. Production variants: expert choice routing, shared experts (DeepSeek), no-aux-loss balancing.
- Expert parallelism (EP) shards experts across devices — see `ai-llm-inference/references/moe-expert-parallelism.md`.

### State Space Model block (Mamba-style)

Subquadratic alternative to attention. Used in hybrid stacks (Jamba, Zamba, Samba) that mix SSM blocks with attention blocks.

```mermaid
flowchart LR
    IN[Input x_t] --> P1[Linear projection]
    P1 --> CONV[1D causal conv<br/>short-range mixing]
    CONV --> ACT[SiLU activation]
    ACT --> SSM[Selective SSM<br/>input-dependent A, B, C, Δ<br/>recurrence: h_t = A h_t-1 + B x_t<br/>output: y_t = C h_t]
    IN --> GATE[Gate branch<br/>linear + SiLU]
    SSM --> MUL((×))
    GATE --> MUL
    MUL --> P2[Linear projection]
    P2 --> OUT[Output y_t]
```

Notes:
- **Linear** in sequence length, **constant** memory per decode step — opposite tradeoff to attention.
- The recurrence is parallelizable at training time via the selective scan kernel.
- Hybrid stacks alternate `SSM block / attention block / SSM block / ...` — SSM handles long-range context cheaply; attention handles precise lookup.

### Vision Transformer (ViT)

How transformers consume images. Foundation for CLIP, SigLIP, and most modern vision-language models.

```mermaid
flowchart LR
    IMG["Image B,3,H,W"] --> PATCH["Patchify 16x16<br/>→ B,N,P²·3"]
    PATCH --> LIN["Linear projection<br/>→ B,N,D"]
    LIN --> CLS["Prepend CLS token"]
    CLS --> POS["+ Positional embedding<br/>learned or 2D RoPE"]
    POS --> ENC["Transformer encoder × L<br/>same block as text<br/>pre-norm, MHA or GQA"]
    ENC --> POOL["CLS token<br/>or global avg pool"]
    POOL --> HEAD["Task head<br/>classification / contrastive / VLM input"]
```

### Diffusion Transformer (DiT) — image/video generation

Replaces U-Net backbone in modern image/video gen models (Stable Diffusion 3, SDXL successors, Sora-class video).

```mermaid
flowchart LR
    Z["Noisy latent z_t<br/>B,C,H,W"] --> PATCH["Patchify → tokens"]
    T[Timestep t] --> TE[Timestep embedding]
    C[Condition: text / class] --> CE[Conditioning embedding]
    TE --> ADAN
    CE --> ADAN
    PATCH --> DiT["DiT block × L<br/>RMSNorm + AdaLN-Zero<br/>self-attn + FFN<br/>conditioned on t,c"]
    ADAN[AdaLN-Zero<br/>per-block scale and shift] --> DiT
    DiT --> UNPATCH[Unpatchify]
    UNPATCH --> EPS["Predicted noise ε̂<br/>or velocity v̂"]
    EPS --> SCHED[Sampler step<br/>DDIM / DPM++ / flow-matching ODE]
    SCHED -. iterate T steps .-> Z
```

Notes:
- **AdaLN-Zero** is the modulation trick — timestep and condition modulate every block's norms.
- **Flow-matching** (rectified flow) has largely replaced DDPM-style training in new models — same architecture, different loss.
- Image gen typically `T = 20–50` steps; distilled / consistency models do it in `1–4`.

### Multimodal Vision-Language Model (LLaVA-style)

How images get into a decoder-only LLM.

```mermaid
flowchart LR
    IMG[Image] --> VIT[Vision encoder<br/>ViT / SigLIP frozen]
    VIT --> VTOK["Visual tokens<br/>B,N_v,D_v"]
    VTOK --> PROJ["Projector<br/>MLP or Q-Former or perceiver<br/>D_v → D_llm"]
    TXT[Text tokens] --> TEMB[LLM embedding]
    PROJ --> CONCAT["Concat: visual ⊕ text tokens"]
    TEMB --> CONCAT
    CONCAT --> LLM[Decoder-only LLM<br/>modern block × N]
    LLM --> OUT[Text response]
```

Notes:
- The **projector** is the trainable bridge — encoder and LLM are often frozen during stage-1 training.
- **Native multimodal** models (Chameleon, Gemini, GPT-4o) skip the projector by training a single transformer on interleaved image/text/audio tokens from scratch.

### Reasoning model training loop (RL-with-CoT)

How o1/o3/R1-class models are trained. Distinct from RLHF — the reward is verifiable correctness, not preference.

```mermaid
flowchart TB
    BASE[Base or SFT model] --> ROLL[Rollout<br/>generate long CoT + answer<br/>per prompt]
    PROMPT[Math / code / reasoning prompts<br/>with verifiable answers] --> ROLL
    ROLL --> JUDGE[Verifier<br/>exact match / unit tests / proof check]
    JUDGE --> REW[Reward signal<br/>1 if correct, 0 if not<br/>+ optional format / length shaping]
    REW --> RL[RL update<br/>GRPO / PPO / REINFORCE++]
    RL --> POL[Updated policy]
    POL -. next rollout .-> ROLL
    POL --> EVAL[Eval on held-out reasoning benches]
```

Notes:
- **GRPO** (group-relative policy optimization) is the dominant choice — drops the value model, normalizes advantages within a sampled group per prompt.
- No human preference labels needed — the verifier replaces RLHF's reward model.
- Long CoTs (10k–100k tokens) make this compute-intensive; throughput optimization matters more than for SFT.

---

## Variants Worth Adding

When the catalog needs to grow:

- **LSTM / GRU cell internals** — gates (forget/input/output) as separate sigmoid/tanh nodes, cell-state line passing through.
- **Attention head detail** — Q,K,V linear projections → `QKᵀ/√d` → softmax → multiply by V. Useful as zoom-in below the modern decoder block.
- **Multi-head vs GQA vs MQA side-by-side** — show the KV-head sharing pattern explicitly; this is the most-asked clarification.
- **RoPE rotation visual** — Q,K rotated in 2D pairs by frequency; harder to draw in Mermaid, may need static image.
- **U-Net** — symmetric encoder–decoder with skip connections; still relevant for medical imaging even though DiT replaced it for generation.
- **Autoencoder / VAE** — VAE adds the `μ, log σ²` split and reparameterization trick.
- **GNN message passing** — one layer of aggregate → transform → update, iterated as "× L".
- **Random Forest / Gradient Boosting** — one tree detailed, then ensemble combiner.
- **Speculative decoding** — draft model proposes k tokens, target verifies in parallel, accept prefix.
- **Encoder–decoder LLM** (T5/Flan style) — for the niche where it still wins (translation, summarization).

## Anti-Patterns

- **Don't draw the math.** Mermaid is bad at matrices. If you need `softmax(QKᵀ/√d)V` shown matrix-by-matrix, switch to LaTeX or a static image.
- **Don't unroll deep stacks.** Show "× N" with one block, not 12 stacked boxes.
- **Don't put hyperparameters in node labels.** Filter counts and dropout rates date a diagram fast — keep them in surrounding prose.
- **Don't combine training and inference in one diagram.** Two side-by-side diagrams beat one with optional dotted arrows.
- **Don't exceed ~25 nodes.** Past that, switch to Excalidraw/Figma, a table, or a notebook with `print(x.shape)` between layers.
