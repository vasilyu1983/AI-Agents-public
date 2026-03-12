# DeepSpeed Inference Template

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
