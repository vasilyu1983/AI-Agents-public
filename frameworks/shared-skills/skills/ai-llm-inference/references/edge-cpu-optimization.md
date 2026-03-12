# Edge & CPU Optimization for LLM Inference

Production patterns for running LLM inference on CPU-only environments, edge devices, and resource-constrained deployments.

## Overview

**When to Use CPU Inference**:
- No GPU available (edge devices, embedded systems)
- Cost-sensitive deployments (CPU hours cheaper than GPU)
- Low-throughput workloads (< 10 QPS)
- Privacy-critical applications (on-device inference)

**Performance Expectations**:
- CPU inference: 5-50x slower than GPU (depends on model size)
- Quantization critical: INT4/INT8 required for acceptable performance
- Optimal for: <13B parameter models
- Not recommended for: Real-time, high-throughput, or large models (>30B)

---

## CPU-Optimized Stacks

### llama.cpp

**Best for**: General-purpose CPU inference, widest model support

**Key features**:
- GGUF format (optimized for CPU)
- Apple Silicon optimizations (Metal)
- SIMD acceleration (AVX2, AVX512, NEON)
- Minimal dependencies

**Installation**:
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make LLAMA_OPENBLAS=1  # With OpenBLAS for faster matmul
```

**Running inference**:
```bash
./main \
  -m models/llama-2-7b.Q4_K_M.gguf \
  -n 256 \
  -t 8 \
  --temp 0.7 \
  --top-p 0.9 \
  -p "Write a poem about AI"
```

**Python bindings**:
```python
from llama_cpp import Llama

llm = Llama(
    model_path="models/llama-2-7b.Q4_K_M.gguf",
    n_ctx=2048,  # Context window
    n_threads=8,  # CPU threads
    n_gpu_layers=0  # CPU only
)

output = llm(
    "Write a poem about AI",
    max_tokens=256,
    temperature=0.7
)
print(output['choices'][0]['text'])
```

### GGML & GGUF Formats

**GGUF = GGML Universal File Format** (current standard as of 2024)

**Quantization types** (ordered by quality/size trade-off):

| Format | Size | Speed | Quality | Use Case |
|--------|------|-------|---------|----------|
| **Q4_K_M** | 4.37 GB | Fast | Good | **Recommended default** |
| **Q4_K_S** | 4.14 GB | Faster | Lower | Speed-critical |
| **Q5_K_M** | 5.13 GB | Medium | Better | Quality-critical |
| **Q6_K** | 5.94 GB | Slower | Best | Near-original quality |
| **Q8_0** | 7.70 GB | Slow | Highest | Minimal quality loss |
| **Q3_K_M** | 3.60 GB | Fastest | Lowest | Ultra-constrained devices |

**Download pre-quantized models**:
```bash
# From HuggingFace
huggingface-cli download \
  TheBloke/Llama-2-7B-GGUF \
  llama-2-7b.Q4_K_M.gguf \
  --local-dir ./models
```

**Quantize your own model**:
```bash
# Convert HuggingFace → GGUF
python convert.py models/llama-2-7b-hf \
  --outtype q4_K_M \
  --outfile models/llama-2-7b.Q4_K_M.gguf
```

### OpenVINO (Intel CPUs)

**Best for**: Intel Xeon, Core processors (optimized for Intel architecture)

**Key features**:
- Intel-specific optimizations (AVX512, AMX, VNNI)
- Model compression (INT8, INT4)
- Graph optimizations (fusion, constant folding)

**Installation**:
```bash
pip install openvino openvino-dev
```

**Model optimization**:
```bash
# Optimize HuggingFace model for CPU
optimum-cli export openvino \
  --model meta-llama/Llama-2-7b-hf \
  --task text-generation \
  --weight-format int4 \
  llama-2-7b-openvino
```

**Running inference**:
```python
from optimum.intel import OVModelForCausalLM
from transformers import AutoTokenizer

model = OVModelForCausalLM.from_pretrained(
    "llama-2-7b-openvino",
    device="CPU"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

inputs = tokenizer("Write a poem", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=256)
print(tokenizer.decode(outputs[0]))
```

### ONNX Runtime

**Best for**: Cross-platform deployment, cloud/edge consistency

**Key features**:
- Cross-platform (Windows, Linux, macOS, ARM)
- Hardware-agnostic optimizations
- Quantization support (INT8, INT4)

**Model conversion**:
```bash
# HuggingFace → ONNX
optimum-cli export onnx \
  --model meta-llama/Llama-2-7b-hf \
  --task text-generation-with-past \
  llama-2-7b-onnx
```

**Quantization**:
```python
from onnxruntime.quantization import quantize_dynamic, QuantType

quantize_dynamic(
    "llama-2-7b-onnx/model.onnx",
    "llama-2-7b-onnx/model_int8.onnx",
    weight_type=QuantType.QInt8
)
```

**Inference**:
```python
from optimum.onnxruntime import ORTModelForCausalLM

model = ORTModelForCausalLM.from_pretrained(
    "llama-2-7b-onnx",
    provider="CPUExecutionProvider"
)
```

### MLC-LLM (Mobile/Edge)

**Best for**: Mobile devices (iOS, Android), WebAssembly

**Key features**:
- Mobile GPU support (Metal, Vulkan)
- WebGPU for browser deployment
- Extreme quantization (3-bit, 4-bit)

**Installation**:
```bash
pip install mlc-llm mlc-ai-nightly
```

**Compile model for mobile**:
```bash
mlc_llm compile \
  meta-llama/Llama-2-7b-hf \
  --target iphone \
  --quantization q4f16_1 \
  --output llama-2-7b-mobile
```

---

## CPU Performance Optimization

### Threading Configuration

**Optimal thread count**:
```python
import os
import multiprocessing

# Rule of thumb: physical cores (not hyperthreads)
num_threads = multiprocessing.cpu_count() // 2

# llama.cpp
os.environ['OMP_NUM_THREADS'] = str(num_threads)

# ONNX Runtime
session_options = onnxruntime.SessionOptions()
session_options.intra_op_num_threads = num_threads
session_options.inter_op_num_threads = 1
```

**Avoid over-threading**:
- Using all threads can cause contention
- Physical cores > hyperthreads for inference
- Test different thread counts for your workload

### SIMD Acceleration

**Check CPU capabilities**:
```bash
# Linux
lscpu | grep -i flags

# macOS
sysctl -a | grep machdep.cpu.features
```

**Enable optimizations**:
- **AVX2**: Standard on modern Intel/AMD (2013+)
- **AVX512**: Intel Xeon Scalable, Ice Lake+
- **AMX**: Intel Sapphire Rapids (4th gen Xeon)
- **NEON**: ARM processors

**Build llama.cpp with optimizations**:
```bash
# Auto-detect SIMD
make LLAMA_NATIVE=1

# Explicit AVX512
make LLAMA_AVX512=1

# Apple Silicon (Metal)
make LLAMA_METAL=1
```

### BLAS Libraries (Matrix Multiplication)

**OpenBLAS** (general purpose):
```bash
make LLAMA_OPENBLAS=1
```

**Intel MKL** (Intel CPUs):
```bash
make LLAMA_MKL=1
```

**Apple Accelerate** (macOS):
```bash
make LLAMA_ACCELERATE=1
```

**Performance impact**: 2-5x speedup for matmul operations

### Memory Bandwidth Optimization

**Use mlock() to prevent swapping**:
```python
# llama.cpp
llm = Llama(
    model_path="model.gguf",
    use_mlock=True  # Lock model in RAM
)
```

**Enable huge pages**:
```bash
# Linux
echo 1024 > /proc/sys/vm/nr_hugepages
```

**Batch size tuning**:
```python
# Larger batches = better throughput (up to memory limit)
llm = Llama(
    model_path="model.gguf",
    n_batch=512  # Default: 512, try 1024-2048
)
```

---

## Edge Device Deployment

### Raspberry Pi (ARM Cortex-A)

**Recommended models**:
- Llama-2-7B-Q3_K_M (3.6 GB) - minimum viable
- TinyLlama-1.1B-Q4_K_M (0.8 GB) - recommended
- Phi-2-Q4_K_M (1.6 GB) - best quality/size

**Configuration**:
```bash
# Build llama.cpp for ARM
make LLAMA_NO_ACCELERATE=1

# Run with limited resources
./main \
  -m TinyLlama-1.1B.Q4_K_M.gguf \
  -n 128 \
  -t 4 \
  --temp 0.7 \
  -c 1024  # Reduce context to save RAM
```

**Performance**: ~5-10 tokens/sec (TinyLlama on Pi 5)

### Mobile Devices (iOS/Android)

**iOS (Swift)**:
```swift
import MLCChat

let model = MLCEngine(
    modelPath: "llama-2-7b-q4f16",
    device: .metal  // Use GPU if available
)

model.generate(
    prompt: "Write a poem",
    maxTokens: 256
) { token in
    print(token, terminator: "")
}
```

**Android (Kotlin)**:
```kotlin
import ai.mlc.mlcllm

val engine = MLCEngine(
    modelPath = "llama-2-7b-q4f16",
    device = Device.VULKAN
)

engine.generate("Write a poem", maxTokens = 256)
```

### Browser (WebAssembly + WebGPU)

**Using Transformers.js**:
```html
<script type="module">
  import { pipeline } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers';

  const generator = await pipeline(
    'text-generation',
    'Xenova/Llama-2-7b-chat-q4',
    { device: 'webgpu' }  // Falls back to WASM
  );

  const output = await generator('Write a poem', {
    max_new_tokens: 256
  });

  console.log(output[0].generated_text);
</script>
```

---

## Benchmarking & Validation

### Performance Testing

**llama.cpp benchmark**:
```bash
./main \
  -m model.gguf \
  -p "Test prompt" \
  -n 128 \
  -t 8 \
  --log-disable

# Output includes:
# - Prompt eval time (prefill)
# - Token generation time (decode)
# - Tokens per second
```

**Expected performance** (7B model, Q4_K_M):

| Hardware | Tokens/Sec | Notes |
|----------|-----------|-------|
| Intel i9-13900K (24 cores) | 30-40 | With AVX512, OpenBLAS |
| AMD Ryzen 9 7950X (16 cores) | 25-35 | With AVX2, OpenBLAS |
| Apple M2 Max (12 cores) | 40-50 | With Metal acceleration |
| Raspberry Pi 5 (4 cores) | 5-10 | With TinyLlama-1.1B |
| iPhone 15 Pro | 15-25 | With MLC-LLM, 4-bit quant |

### Quality Validation

**Test quantization impact**:
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Original model
model_fp16 = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16
)

# Test prompts
prompts = [
    "What is the capital of France?",
    "Write a Python function to calculate fibonacci",
    "Explain quantum computing in simple terms"
]

# Compare outputs (original vs quantized)
# Run both models and check:
# 1. Factual correctness
# 2. Coherence
# 3. Instruction following
```

### Validation Checklist

- [ ] Quantization format selected (Q4_K_M recommended)
- [ ] Threading tuned (num_threads = physical cores)
- [ ] SIMD acceleration enabled (check compilation flags)
- [ ] BLAS library selected (OpenBLAS/MKL/Accelerate)
- [ ] Batch size optimized (test 512, 1024, 2048)
- [ ] Memory locked (use_mlock=True)
- [ ] Performance benchmarked (tokens/sec measured)
- [ ] Quality validated (compare vs FP16 baseline)
- [ ] Context window sized appropriately (reduce if memory-constrained)

---

## Production Deployment Patterns

### Serverless CPU Inference

**AWS Lambda example**:
```python
# Lambda handler with llama.cpp
import ctypes
from llama_cpp import Llama

# Load model at cold start (outside handler)
llm = Llama(
    model_path="/opt/model.gguf",  # Lambda layer
    n_ctx=1024,
    n_threads=2,  # Lambda CPU limit
    use_mmap=True,
    use_mlock=False  # Lambda doesn't support mlock
)

def handler(event, context):
    prompt = event['prompt']
    output = llm(prompt, max_tokens=128)
    return {
        'statusCode': 200,
        'body': output['choices'][0]['text']
    }
```

**Considerations**:
- Cold start: 10-30s (model loading)
- Memory limit: 10GB max (use Q3/Q4 quantization)
- CPU: 2-6 vCPUs (limited parallelism)
- Cost: $0.0000166667/GB-sec

### Docker Container

**Dockerfile**:
```dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    wget

# Build llama.cpp
WORKDIR /app
RUN git clone https://github.com/ggerganov/llama.cpp && \
    cd llama.cpp && \
    make LLAMA_OPENBLAS=1

# Copy model
COPY model.Q4_K_M.gguf /app/model.gguf

# Run server
CMD ["./llama.cpp/server", "-m", "/app/model.gguf", "-c", "2048", "-t", "8"]
```

**Kubernetes deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-cpu-inference
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: llama
        image: llm-cpu-inference:latest
        resources:
          requests:
            cpu: "8000m"
            memory: "16Gi"
          limits:
            cpu: "8000m"
            memory: "16Gi"
```

---

## Common Issues & Troubleshooting

**Problem**: Slow token generation (< 5 tok/s)
- Check: Thread count too high or too low
- Check: SIMD not enabled (recompile with LLAMA_NATIVE=1)
- Fix: Use smaller model or better quantization

**Problem**: Model doesn't fit in RAM
- Check: Model size vs available memory
- Fix: Use more aggressive quantization (Q4 → Q3)
- Fix: Reduce context window (n_ctx)

**Problem**: Poor quality with Q3/Q4
- Check: Quantization type (try Q4_K_M instead of Q4_0)
- Fix: Use Q5_K_M or Q6_K for critical applications

**Problem**: Crashes on ARM devices
- Check: NEON support in binary (recompile if needed)
- Fix: Reduce batch size and context window

---

## References

- llama.cpp: https://github.com/ggerganov/llama.cpp
- GGUF Specification: https://github.com/ggerganov/ggml/blob/master/docs/gguf.md
- OpenVINO: https://docs.openvino.ai/latest/home.html
- ONNX Runtime: https://onnxruntime.ai/docs/
- MLC-LLM: https://llm.mlc.ai/
- TheBloke GGUF Models: https://huggingface.co/TheBloke
