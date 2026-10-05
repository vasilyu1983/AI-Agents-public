# GGUF Deployment Template

Use this for CPU, edge, desktop, or Apple Silicon inference with llama.cpp-compatible GGUF models.

## 1. Model Package

```yaml
model:
  source_repo: "<huggingface-or-local-path>"
  gguf_file: "<model-q4_k_m.gguf>"
  tokenizer: "<bundled-or-explicit>"
  chat_template: "<if-custom>"
```

## 2. Runtime Settings

```yaml
runtime:
  n_ctx: 8192
  n_threads: <cpu_threads>
  n_batch: 512
  n_ubatch: 128
  n_gpu_layers: 0
  flash_attn: false
  temperature: 0.2
  top_p: 0.95
```

## 3. Launch Example

```bash
./llama-server \
  -m /models/<model-q4_k_m.gguf> \
  --ctx-size 8192 \
  --threads <cpu_threads> \
  --batch-size 512 \
  --ubatch-size 128 \
  --n-gpu-layers 0 \
  --host 0.0.0.0 \
  --port 8080
```

## 4. Quant Level Rules

- `Q4_K_M`: default starting point for constrained devices
- `Q5_K_M`: higher quality when memory allows
- `Q6_K`: stronger quality retention with moderate memory increase
- `Q8_0`: near-full precision edge deployment when RAM is available

## 5. Validation Checklist

- [ ] prompt template matches the target model family
- [ ] tokenizer and rope settings are correct
- [ ] TTFT and tokens per second measured on target hardware
- [ ] structured-output tasks re-tested if the app requires them
- [ ] memory headroom measured after warmup
