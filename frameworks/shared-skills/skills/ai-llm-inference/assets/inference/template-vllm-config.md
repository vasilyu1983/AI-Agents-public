# vLLM Inference Configuration Template

Complete config for deploying an LLM using vLLM with continuous batching.

---

## 1. Model

model: "<model_name_or_path>"
dtype: "bfloat16"
tokenizer: "<tokenizer_path>"
trust_remote_code: false
tensor_parallel_size: <num_gpus>

---

## 2. Runtime

runtime:
max_num_seqs: 512
max_model_len: <max_context> # e.g. 4096, 8192, 32768
gpu_memory_utilization: 0.90
disable_log_requests: true

---

## 3. Batching (Continuous)

batching:
enable: true
max_tokens: <value> # tune dynamically
scheduler_policy: "token"

---

## 4. Logging

logging:
level: "info"
log_metrics: true
log_requests: false

---

## 5. Server

server:
host: "0.0.0.0"
port: 8000
enable_cors: true

---

## 6. Health Checks

- Startup: ensure model loads  
- Liveness: GPU accessible  
- Readiness: warm cache populated  

---

## 7. Checklist

- [ ] vLLM installed  
- [ ] GPU memory fits model  
- [ ] Batching load-tested  
- [ ] Token throughput measured  