# High Throughput Serving Setup (vLLM/TensorRT-LLM)

Configuration template for large-scale production serving.

---

## 1. Infra Setup

- GPU class: <A100/H100/L40>  
- Replicas: <N>  
- Autoscaling rules:  
  - CPU/GPU > 70%  
  - Queue length > threshold  

---

## 2. Runtime Settings

runtime:
batching: continuous
kv_cache: "fp16"
max_context: <max_tokens>
prefill_optimization: true

---

## 3. Load Balancing

- Sticky routing optional  
- Prefer weighted round-robin  
- Health checks every 5 seconds  

---

## 4. Observability

Dashboards must include:

- Token throughput  
- Latency percentiles  
- GPU utilization  
- Request queue depth  
- KV cache hit ratio  

---

## 5. Failure Handling

- Fallback to smaller model  
- Reject long inputs  
- Autoscale aggressively during surges  
