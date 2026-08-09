# TensorRT-LLM Inference Config Template

Optimized configuration for high-performance, low-latency inference on NVIDIA GPUs.

---

## 1. Model

model: "<hf_model_path>"
precision: "fp8" # or fp16/int8
tensor_parallel_size: <num_gpus>
pipeline_parallel_size: 1

---

## 2. Engine Settings

engine:
max_batch_size: 32
max_input_len: <len>
max_output_len: <len>
enable_refit: false
use_parallel_embeddings: true

---

## 3. Attention Optimization

attention:
type: "flash" # flash | paged | default
kv_cache_quant: "int8"

---

## 4. Kernel Optimization

kernels:
enable_fused_mlp: true
enable_sparsity: false

---

## 5. Serving

server:
grpc_port: 9000
http_port: 8000
num_workers: 4

---

## 6. Checklist

- [ ] Engine built successfully  
- [ ] Precision validated  
- [ ] Latency measured on representative inputs  
