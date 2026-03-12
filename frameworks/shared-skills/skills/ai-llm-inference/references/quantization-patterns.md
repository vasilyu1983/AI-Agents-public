# Quantization Patterns for LLM Inference

Operational guidance for selecting and applying quantization techniques to reduce
GPU/CPU memory usage and latency while maintaining acceptable quality.

**Updated January 2026**: FP8 now recommended as first choice on supported hardware. INT8 not supported on Blackwell GPUs.

---

## Critical: Hardware Compatibility

| GPU Architecture | Compute Capability | FP8 | INT8 | INT4 |
|------------------|-------------------|-----|------|------|
| **Blackwell (B200, B100)** | 100+ | Yes | **NO** | Yes |
| **Hopper (H100, H200)** | 90 | Yes | Yes | Yes |
| **Ada Lovelace (RTX 4090)** | 89 | Yes | Yes | Yes |
| **Ampere (A100, A10)** | 80-86 | No | Yes | Yes |

**Blackwell Limitation**: INT8 quantization is not supported on compute capability >= 100. Use FP8 instead.

---

## 1. Quick Decision Table

| Goal | Recommended Quantization | Hardware Notes |
|------|---------------------------|----------------|
| **First choice (2026)** | FP8 | Hopper/Ada/Blackwell only |
| **Max speed + smallest memory** | INT4 (GPTQ, AWQ, GGUF Q4_K_M) | All GPUs |
| **Good stability, minimal loss** | FP8 > INT8 SmoothQuant | FP8 preferred |
| **CPU or edge inference** | GGUF (Q4_K_M / Q6_K / Q8_0) | CPU/Metal |
| **GPU + high-quality** | GPTQ or AWQ weight-only | All GPUs |
| **Safety-critical** | FP8 or INT8 (avoid INT4) | Check hardware |
| **Blackwell GPUs** | FP8 or INT4 | **No INT8** |

**NVIDIA Recommendation**: "Prioritize using FP8 first, as we typically see it offers the best performance and accuracy. If results do not meet your use case, experiment with INT8 SmoothQuant followed by AWQ/GPTQ."

---

## 1.5. FP8 Quantization (Recommended First Choice)

### Why FP8 First (2025+)

- **Higher dynamic range** than INT8 (better for activations and KV cache)
- **33% faster inference** on supported hardware
- **Lower memory footprint**: 7GB VRAM for Mistral 7B vs 16GB FP16
- **2.3x inference speedup** at batch size 16 vs FP16 on H100

### FP8 vs INT8 Comparison

| Aspect | FP8 | INT8 |
|--------|-----|------|
| Dynamic range | Higher | Lower |
| Accuracy impact | Lower | Higher |
| Blackwell support | Yes | **No** |
| KV cache quantization | Recommended | Fallback only |
| Calibration needs | Simpler | More sensitive |

### When to Use FP8

- Hopper (H100, H200), Ada (RTX 4090), or Blackwell GPUs
- KV cache quantization needed
- Want best accuracy/performance tradeoff
- Serving models where quality matters

### FP8 Configuration (vLLM)

```bash
vllm serve meta-llama/Llama-3-70B \
    --quantization fp8 \
    --kv-cache-dtype fp8
```

### FP8 Configuration (TensorRT-LLM)

```python
from tensorrt_llm.quantization import QuantMode
quant_mode = QuantMode.FP8
```

**Checklist - FP8 Quantization**
- [ ] Verify GPU supports FP8 (Hopper/Ada/Blackwell)
- [ ] Start with 512 samples for calibration
- [ ] Enable FP8 KV cache for 2-3x larger batch sizes
- [ ] Validate on representative eval set
- [ ] Compare latency vs FP16 baseline

---

## 2. Weight-Only Quantization

### Use when:
- You need aggressive compression  
- You’re serving models > 7B  
- You want to minimize VRAM without retraining  

### Operational Notes:
- GPTQ / AWQ recommended  
- Calibration dataset: 128–512 samples  
- Check per-layer error (some layers sensitive)

**Checklist – Weight-Only Quantization**
- [ ] Calibration dataset prepared  
- [ ] Per-layer quantization error inspected  
- [ ] Model loads without kernel mismatches  
- [ ] Output stability tested on eval suite  

---

## 3. Activation-Aware Quantization (INT8)

### Use when:
- You want safer quantization  
- Model must maintain >95% of original quality  

### BitsAndBytes INT8 Guidelines:
- Avoid quantizing small hidden layers  
- Ensure GPU supports INT8 tensor cores  
- Test long context windows

**Checklist – INT8**
- [ ] Evaluate on large context  
- [ ] Validate layernorm stability  
- [ ] No loss spikes on safety tasks  

---

## 4. 4-bit QLoRA-Optimized Models

When training LoRA adapters, use **NF4** quantization.

### Operation:
- Base model: 4-bit quantized  
- Adapters: FP16/BF16  
- Memory savings: 4×–8×  
- Inference quality: depends on merge

---

## 5. GGUF / CPU & Edge Formats

### Recommended formats:
- **Q4_K_M** — best balance  
- **Q6_K** — higher quality  
- **Q8_0** — stable + CPU-friendly  

**Checklist – GGUF**
- [ ] Convert with llama.cpp converters  
- [ ] Ensure correct rope scaling & tokenizer  
- [ ] Benchmark with 1, 2, 4 threads  

---

## 6. KV Cache Quantization

Reduces memory pressure for long-context inference. **FP8 KV cache now recommended over INT8.**

### FP8 vs INT8 KV Cache

| Aspect | FP8 KV Cache | INT8 KV Cache |
|--------|--------------|---------------|
| Accuracy impact | Lower | Higher |
| Batch size gain | 2-3x larger | 1.5-2x larger |
| Hopper/Ada support | Yes | Yes |
| Blackwell support | Yes | **No** |
| Recommendation | **First choice** | Fallback only |

### When to Use FP8 KV Cache

- Hopper or Ada GPUs with long-context workloads
- Want maximum batch size without quality loss
- RAG or multi-turn chat with large context windows

### Configuration

```bash
# vLLM with FP8 KV cache
vllm serve model --kv-cache-dtype fp8

# TensorRT-LLM
--kv_cache_type fp8
```

### Notes

- FP8 KV cache enables 2-3x larger batch sizes on H100
- At 8K context, LLaMA-3 70B consumes ~20GB KV cache per request
- FP8 KV cache has lower accuracy impact than INT8 in most cases
- Test long-chunk RAG workloads before production  

---

## 7. Final Quantization Validation

- [ ] Run full regression suite  
- [ ] Compare latency difference  
- [ ] Compare quality difference (<2% drop target)  
- [ ] Validate on adversarial and long-context prompts  
