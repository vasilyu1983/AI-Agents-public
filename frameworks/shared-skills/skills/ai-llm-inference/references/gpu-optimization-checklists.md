# GPU Optimization Checklists

Actionable diagnostics for maximizing GPU throughput, token speed, and resource efficiency.

**Updated January 2026**: Added Blackwell (B200, GB200) benchmarks and H200 comparisons.

---

## 0. GPU Hardware Comparison (2026)

### Performance Benchmarks

| GPU | Memory | LLM Inference vs H100 | Best For |
|-----|--------|----------------------|----------|
| **GB200 NVL72** | 180GB HBM3e × 72 | **30x** | Data center scale |
| **B200** | 180GB HBM3e | **11-15x** | Maximum single-GPU |
| **H200** | 141GB HBM3e | 1.5-2x | Production standard |
| **H100** | 80GB HBM3 | 1x (baseline) | Mature ecosystem |
| **A100** | 80GB HBM2e | 0.5x | Cost-effective |

### Blackwell-Specific Benchmarks (B200/GB200)

**DeepSeek-R1 on GB200 NVL72**:

- 26k input tokens/sec per GPU (prefill)
- 13k output tokens/sec per GPU (decode)
- 4x performance vs H100/H200

**Key Blackwell Optimizations**:

- FP8 attention (required - INT8 not supported)
- NVFP4 MoE quantization
- 5th gen tensor cores
- NVLink 5 (faster GPU-to-GPU)
- TMA (Tensor Memory Accelerator)

### H200 vs H100

| Aspect | H200 | H100 |
|--------|------|------|
| Memory | 141GB HBM3e | 80GB HBM3 |
| Bandwidth | 4.8 TB/s | 3.35 TB/s |
| Batch size | 1.8x larger | Baseline |
| Software stack | Same as H100 | Mature |

**Recommendation**: H200 for production serving today. B200/GB200 for maximum performance when available.

### Software Requirements by GPU

| GPU | CUDA | cuDNN | Frameworks |
|-----|------|-------|------------|
| **Blackwell** | 12.4+ | 9+ | vLLM, SGLang, TensorRT-LLM (latest) |
| **Hopper** | 12.0+ | 8+ | All frameworks |
| **Ampere** | 11.8+ | 8+ | All frameworks |

---

## 1. GPU Profiling Checklist

- [ ] GPU utilization > 70% for steady-state workloads  
- [ ] No long idle gaps between tokens  
- [ ] NVLink / PCIe bandwidth not saturated  
- [ ] Memory fragmentation low (<10%)  
- [ ] Kernel launches efficient (no micro-kernel spam)  

---

## 2. Memory Optimization Checklist

- [ ] Enable FlashAttention / xFormers  
- [ ] Enable fused kernels where available  
- [ ] Quantize model to INT8 or INT4  
- [ ] Reduce KV cache memory (8-bit KV cache)  
- [ ] Reduce max sequence length if possible  

---

## 3. Latency Optimization Checklist

- [ ] Use TensorRT-LLM kernels  
- [ ] Disable Python overhead with C++ runtime when needed  
- [ ] Use pinned memory for CPU→GPU transfers  
- [ ] Preload model and warm caches  

---

## 4. Throughput Optimization Checklist

- [ ] Enable continuous batching  
- [ ] Increase batch size incrementally  
- [ ] Use multiple replicas behind LB  
- [ ] Use multi-GPU tensor parallel if model too large  
- [ ] Avoid blocking CPU workloads on GPU thread  

---

## 5. Cost Optimization Checklist

- [ ] Right-size GPU type (L40, A100, H100)  
- [ ] Use quantized models  
- [ ] Cap output tokens  
- [ ] Cache high-frequency prompts/responses  
- [ ] Use spot/preemptible instances when safe  

---

## 6. Production GPU Health Monitoring

Monitor:

- Utilization  
- Memory usage  
- Temperature  
- Kernel exec time  
- Queue backlog  
- Token throughput per replica

**Alerts**

- [ ] GPU OOM  
- [ ] Sustained low utilization  
- [ ] Temperature > 85°C  
