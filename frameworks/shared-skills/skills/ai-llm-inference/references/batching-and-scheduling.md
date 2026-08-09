# Batching & Scheduling for LLM Inference

Batching is the #1 source of throughput improvement. These patterns ensure efficient GPU utilization.

---

## 1. Continuous Batching (vLLM Pattern)

### Behavior

- Incoming requests join ongoing batch  
- No batch boundary waits  
- Token-level scheduling  

### Benefits

- Massive QPS gains  
- Low latency growth  
- Excellent for chatbots and APIs  

**Checklist**

- [ ] Continuous batching enabled  
- [ ] Max batch size tuned  
- [ ] Scheduling policy tested  

---

## 2. Static Batching

Use for predictable batch workloads such as:

- Offline summarization  
- Large dataset scoring  
- Periodic batch jobs  

**Notes:**

- Largest gains when input length similar across items  
- Use fixed batch sizes (e.g., 16, 32, 64)

---

## 3. Priority Scheduling

### Use when

- Mixture of real-time and low-priority jobs  

### Strategy

- Assign request classes  
- Allow preemption  
- Ensure latency-sensitive jobs bypass batch queue  

**Checklist**

- [ ] Priority classes defined  
- [ ] Preemption rules tested  
- [ ] No starvation of low-priority requests  

---

## 4. Token-by-Token Scheduling

Enabled by vLLM and specialized runtimes.

### Benefits

- Tiny idle gaps between tokens  
- Better time slicing  
- Smooth multi-request performance  

---

## 5. Batching Tuning Guidelines

- Start with batch size 8 → scale until GPU saturates  
- Monitor:
  - GPU utilization  
  - Token throughput (tok/s)  
  - Latency at P95  

**Checklist**

- [ ] Throughput measured  
- [ ] Latency budget respected  
- [ ] Batch size auto-tuning scripted  
