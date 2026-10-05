# DeepSpeed Inference Template

> **Scope**: DeepSpeed inference is viable for ZeRO-Offload / very-large-model sharding where GPU memory is the hard constraint and latency is secondary. It is **not** the recommended production token-serving path for interactive or high-throughput workloads. For production token serving, prefer vLLM V1, SGLang, or TensorRT-LLM. Use DeepSpeed inference when its ZeRO-Offload or pipeline-parallel sharding capabilities are specifically required and alternatives cannot fit the model.

Configuration for serving LLMs with DeepSpeed-MII or DeepSpeed-Inference.

---

## 1. Environment

ds_version: "0.16+"
torch_version: "2.9+"

---

## 2. Model Settings

model:
name: "<model_path>"
dtype: "bf16"
tensor_parallel:
size: <num_gpus>
quantization:
enable: false

---

## 3. Runtime Settings

runtime:
max_context: <max_tokens>
enable_kv_cache: true
kv_cache_quantization: "int8"
use_cuda_graph: true

---

## 4. Launch Config

launch:
hostfile: "./hostfile"
deepspeed_port: 29500
num_nodes: <nodes>

---

## 5. Checklist

- [ ] CUDA graph enabled  
- [ ] Multi-GPU tested  
- [ ] KV offloading configured when needed  
