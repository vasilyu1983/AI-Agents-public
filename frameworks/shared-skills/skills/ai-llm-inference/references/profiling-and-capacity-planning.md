# Profiling, Benchmarking & Capacity Planning

Production-grade methodologies for measuring LLM inference performance, establishing performance budgets, and planning infrastructure capacity.

## Overview

**Why profiling matters**:
- Establish performance baselines
- Identify bottlenecks (GPU, CPU, memory, network)
- Validate optimization impact
- Set capacity planning targets
- Prevent performance regressions

**Key metrics**:
- **Latency**: Time to first token (TTFT), time per token
- **Throughput**: Tokens/second, queries/second (QPS)
- **Goodput**: Useful tokens/second (excludes failed/timeout requests)
- **GPU Utilization**: Compute, memory bandwidth, tensor core usage
- **Memory Headroom**: Available vs allocated vs used

---

## Load Generation & Benchmarking

### Workload Characterization

**Capture production patterns**:
```python
# Sample real production traffic
import pandas as pd

# Log: timestamp, prompt_len, completion_len, latency
logs = pd.read_csv('production_logs.csv')

# Analyze distributions
print(logs['prompt_len'].describe())
print(logs['completion_len'].describe())

# Distribution percentiles
p50_prompt = logs['prompt_len'].quantile(0.50)
p95_prompt = logs['prompt_len'].quantile(0.95)
p99_prompt = logs['prompt_len'].quantile(0.99)

print(f"Prompt lengths: p50={p50_prompt}, p95={p95_prompt}, p99={p99_prompt}")
```

**Example distributions** (ChatGPT-like workload):
- Prompt lengths: p50=150, p95=800, p99=2000 tokens
- Completion lengths: p50=100, p95=500, p99=1500 tokens
- QPS pattern: baseline 100 QPS, peak 500 QPS (5x burst)

### Load Testing with vLLM Benchmark

**Built-in benchmark tool**:
```bash
# Install vLLM
pip install vllm

# Run benchmark
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-13b-hf \
  --tensor-parallel-size 2 &

# Benchmark with realistic workload
python benchmarks/benchmark_serving.py \
  --backend vllm \
  --model meta-llama/Llama-2-13b-hf \
  --dataset-name sharegpt \
  --num-prompts 1000 \
  --request-rate 10 \
  --seed 42
```

**Custom load generator**:
```python
import asyncio
import aiohttp
import time
import random

async def send_request(session, prompt, url="http://localhost:8000/v1/completions"):
    payload = {
        "model": "meta-llama/Llama-2-13b-hf",
        "prompt": prompt,
        "max_tokens": 256,
        "temperature": 0.7
    }
    start = time.time()
    async with session.post(url, json=payload) as response:
        result = await response.json()
        latency = time.time() - start
        return latency, len(result['choices'][0]['text'].split())

async def load_test(qps, duration_sec, prompts):
    """
    qps: target queries per second
    duration_sec: how long to run test
    prompts: list of test prompts
    """
    interval = 1.0 / qps
    latencies = []
    token_counts = []

    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        while time.time() - start_time < duration_sec:
            prompt = random.choice(prompts)
            task = send_request(session, prompt)

            # Fire and forget (async)
            asyncio.create_task(task)

            await asyncio.sleep(interval)

    return latencies, token_counts

# Run load test
prompts = ["Write a poem", "Explain quantum physics", "Code review this: ..."]
asyncio.run(load_test(qps=50, duration_sec=300, prompts=prompts))
```

### Metrics Collection

**Capture key metrics**:
```python
import numpy as np
from dataclasses import dataclass
from typing import List

@dataclass
class BenchmarkMetrics:
    latencies: List[float]  # seconds
    token_counts: List[int]
    gpu_utils: List[float]  # percentage
    memory_used: List[float]  # GB

    def analyze(self):
        return {
            # Latency percentiles
            'latency_p50': np.percentile(self.latencies, 50),
            'latency_p95': np.percentile(self.latencies, 95),
            'latency_p99': np.percentile(self.latencies, 99),
            'latency_max': np.max(self.latencies),

            # Throughput
            'total_tokens': np.sum(self.token_counts),
            'duration': np.sum(self.latencies),
            'throughput_tps': np.sum(self.token_counts) / np.sum(self.latencies),

            # Goodput (exclude timeouts/errors)
            'success_rate': len([l for l in self.latencies if l < 30]) / len(self.latencies),
            'goodput_tps': np.sum(self.token_counts) * self.success_rate / np.sum(self.latencies),

            # Resource utilization
            'gpu_util_avg': np.mean(self.gpu_utils),
            'gpu_util_p95': np.percentile(self.gpu_utils, 95),
            'memory_used_avg': np.mean(self.memory_used),
            'memory_used_max': np.max(self.memory_used)
        }
```

**Example output**:
```
Latency (seconds):
  p50: 0.85
  p95: 2.10
  p99: 4.50
  max: 8.20

Throughput:
  Total tokens: 245,000
  Duration: 300s
  Tokens/sec: 817

Goodput:
  Success rate: 98.5%
  Goodput: 805 tokens/sec

GPU Utilization:
  Average: 87%
  p95: 94%
  Memory used (avg): 38GB
  Memory used (max): 42GB
```

---

## Performance Budgets & SLOs

### Define Service Level Objectives

**Example SLOs**:
```yaml
# Production SLO definition
slos:
  latency:
    p50: 500ms
    p95: 2000ms
    p99: 5000ms

  throughput:
    min_qps: 100
    target_qps: 500
    burst_qps: 1000

  availability:
    uptime: 99.9%  # 43 min/month downtime

  quality:
    success_rate: 99%  # <1% errors/timeouts

  cost:
    cost_per_1m_tokens: $5.00
```

### Establishing Performance Budgets

**Token budget example**:
```python
# Define budgets based on SLOs
budgets = {
    'prefill_latency_ms': 200,  # Time to process prompt
    'decode_latency_ms': 20,    # Time per output token
    'max_batch_size': 64,
    'max_context_len': 8192,
    'gpu_memory_gb': 40,
    'cost_per_1m_tokens': 5.0
}

# Validate configuration meets budgets
def validate_budgets(config, budgets, benchmark_results):
    violations = []

    if benchmark_results['latency_p95'] > budgets['max_latency_p95']:
        violations.append(f"P95 latency {benchmark_results['latency_p95']}s exceeds budget {budgets['max_latency_p95']}s")

    if benchmark_results['memory_used_max'] > budgets['gpu_memory_gb']:
        violations.append(f"Memory {benchmark_results['memory_used_max']}GB exceeds budget {budgets['gpu_memory_gb']}GB")

    if violations:
        raise Exception(f"Budget violations: {violations}")

    return True
```

---

## Capacity Planning

### Replica Count Derivation

**Calculate required replicas**:
```python
def calculate_replicas(
    target_qps: float,
    tokens_per_request: int,
    latency_budget_sec: float,
    tokens_per_sec_per_replica: float,
    safety_margin: float = 0.3  # 30% headroom
):
    """
    Derive number of replicas needed to meet QPS target.

    Example:
      - Target: 500 QPS
      - Avg response: 200 tokens
      - Latency budget: 2s
      - Single replica throughput: 800 tok/s
      - Safety margin: 30%

    Required throughput = 500 QPS × 200 tokens = 100,000 tok/s
    Per-replica capacity = 800 tok/s
    Replicas needed = ceil(100,000 / 800) = 125 replicas
    With 30% margin = 125 × 1.3 = 163 replicas
    """
    required_throughput = target_qps * tokens_per_request
    replicas = required_throughput / tokens_per_sec_per_replica
    replicas_with_margin = replicas * (1 + safety_margin)

    return {
        'required_throughput_tps': required_throughput,
        'replicas_min': int(np.ceil(replicas)),
        'replicas_recommended': int(np.ceil(replicas_with_margin)),
        'cost_per_hour': int(np.ceil(replicas_with_margin)) * 3.67  # A100 hourly
    }

# Example calculation
plan = calculate_replicas(
    target_qps=500,
    tokens_per_request=200,
    latency_budget_sec=2.0,
    tokens_per_sec_per_replica=800
)

print(f"Required replicas: {plan['replicas_recommended']}")
print(f"Estimated cost: ${plan['cost_per_hour']}/hour")
```

### Autoscaling Policies

**Kubernetes HPA config**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-inference
  minReplicas: 5
  maxReplicas: 50
  metrics:
  # Scale on custom latency metric
  - type: Pods
    pods:
      metric:
        name: inference_latency_p95
      target:
        type: AverageValue
        averageValue: "2000m"  # 2s in milliseconds

  # Scale on queue depth
  - type: Pods
    pods:
      metric:
        name: request_queue_depth
      target:
        type: AverageValue
        averageValue: "10"

  # Scale on GPU utilization
  - type: Resource
    resource:
      name: nvidia.com/gpu
      target:
        type: Utilization
        averageUtilization: 80

  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60

    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5min before scaling down
      policies:
      - type: Percent
        value: 25
        periodSeconds: 60
```

### KV Cache Size Planning

**Calculate cache requirements**:
```python
def calculate_kv_cache_size(
    num_layers: int,
    batch_size: int,
    max_context_len: int,
    hidden_size: int,
    num_heads: int,
    dtype_bytes: int  # 2 for FP16, 1 for FP8
):
    """
    KV cache size = 2 (K+V) × num_layers × batch_size × seq_len × hidden_size × dtype

    Example: Llama-2-13B
      - Layers: 40
      - Batch: 64
      - Context: 4096
      - Hidden: 5120
      - Heads: 40
      - dtype: FP16 (2 bytes)

    Size = 2 × 40 × 64 × 4096 × 5120 × 2 bytes
         = 2 × 40 × 64 × 4096 × 5120 × 2 / (1024^3)
         = 80GB
    """
    size_bytes = 2 * num_layers * batch_size * max_context_len * hidden_size * dtype_bytes
    size_gb = size_bytes / (1024**3)

    return {
        'kv_cache_gb': size_gb,
        'per_sequence_mb': (size_bytes / batch_size) / (1024**2),
        'total_memory_gb': size_gb * 1.2  # Add 20% overhead
    }

# Example: Llama-2-13B
cache = calculate_kv_cache_size(
    num_layers=40,
    batch_size=64,
    max_context_len=4096,
    hidden_size=5120,
    num_heads=40,
    dtype_bytes=2  # FP16
)

print(f"KV cache size: {cache['kv_cache_gb']:.1f} GB")
print(f"Per sequence: {cache['per_sequence_mb']:.1f} MB")
print(f"Total memory needed: {cache['total_memory_gb']:.1f} GB")
```

---

## Regression Guards & CI/CD Integration

### Performance Testing in CI

**GitHub Actions example**:
```yaml
name: Performance Regression Test

on: [pull_request]

jobs:
  benchmark:
    runs-on: [self-hosted, gpu]
    steps:
    - uses: actions/checkout@v3

    - name: Run benchmark
      run: |
        python benchmarks/benchmark_inference.py \
          --model ${{ matrix.model }} \
          --output results.json

    - name: Check performance budgets
      run: |
        python scripts/check_budgets.py \
          --results results.json \
          --budgets budgets.yaml

    - name: Fail if regression
      run: |
        if [ $? -ne 0 ]; then
          echo "Performance regression detected!"
          exit 1
        fi
```

**Budget validation script**:
```python
# scripts/check_budgets.py
import json
import yaml
import sys

def check_budgets(results_file, budgets_file):
    with open(results_file) as f:
        results = json.load(f)

    with open(budgets_file) as f:
        budgets = yaml.safe_load(f)

    violations = []

    # Check latency budget
    if results['latency_p95'] > budgets['latency_p95_ms'] / 1000:
        violations.append(
            f"P95 latency {results['latency_p95']:.2f}s exceeds "
            f"budget {budgets['latency_p95_ms']/1000:.2f}s"
        )

    # Check throughput budget
    if results['throughput_tps'] < budgets['min_throughput_tps']:
        violations.append(
            f"Throughput {results['throughput_tps']:.0f} tok/s below "
            f"budget {budgets['min_throughput_tps']} tok/s"
        )

    # Check cost budget
    if results['cost_per_1m_tokens'] > budgets['max_cost_per_1m_tokens']:
        violations.append(
            f"Cost ${results['cost_per_1m_tokens']:.2f}/1M tokens exceeds "
            f"budget ${budgets['max_cost_per_1m_tokens']:.2f}/1M"
        )

    if violations:
        print("[FAIL] Performance budget violations:")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)
    else:
        print("[OK] All performance budgets met")
        sys.exit(0)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', required=True)
    parser.add_argument('--budgets', required=True)
    args = parser.parse_args()

    check_budgets(args.results, args.budgets)
```

### Benchmark Report Storage

**Store with config hash**:
```python
import hashlib
import json
from datetime import datetime

def store_benchmark(config, results):
    # Generate config hash
    config_str = json.dumps(config, sort_keys=True)
    config_hash = hashlib.sha256(config_str.encode()).hexdigest()[:8]

    # Create report
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'config_hash': config_hash,
        'config': config,
        'results': results,
        'git_commit': os.popen('git rev-parse HEAD').read().strip()
    }

    # Store in database/S3/filesystem
    filename = f"benchmarks/{config_hash}_{report['timestamp']}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)

    return filename
```

---

## Profiling Tools & Techniques

### GPU Profiling with nvidia-smi

**Monitor in real-time**:
```bash
# Watch GPU metrics (1s refresh)
nvidia-smi dmon -s pucvmet -d 1

# Fields:
# - pwr: Power usage
# - gtemp: GPU temperature
# - sm: SM (streaming multiprocessor) utilization
# - mem: Memory utilization
# - enc: Encoder utilization
# - dec: Decoder utilization
# - mclk: Memory clock
# - pclk: Graphics clock
```

**Log to file**:
```bash
# Continuous logging
nvidia-smi dmon -s pucvmet -d 1 -f gpu_metrics.log &

# Stop logging
pkill nvidia-smi
```

### CUDA Profiling with Nsight

**Profile kernel execution**:
```bash
# Install Nsight Systems
# Download from: https://developer.nvidia.com/nsight-systems

# Profile inference
nsys profile \
  --trace=cuda,nvtx,osrt \
  --output=inference_profile \
  python inference_script.py

# View in GUI
nsys-ui inference_profile.nsys-rep
```

**Annotate code with NVTX**:
```python
import torch

# Mark regions
with torch.cuda.nvtx.range("model_forward"):
    outputs = model(inputs)

with torch.cuda.nvtx.range("postprocess"):
    result = postprocess(outputs)
```

### Python Profiling

**cProfile for CPU bottlenecks**:
```python
import cProfile
import pstats

def profile_inference():
    profiler = cProfile.Profile()
    profiler.enable()

    # Run inference
    output = model.generate(prompt)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

profile_inference()
```

---

## Checklist: Performance Validation Complete

- [ ] Benchmark report stored with config/model hash
- [ ] Goodput and latency within SLO budgets
- [ ] GPU utilization > 80% (not under-utilized)
- [ ] Memory headroom > 10% (not at limit)
- [ ] Replica count calculated from QPS target
- [ ] Capacity plan documented (replicas, autoscaling policies)
- [ ] KV cache size validated for max batch + context
- [ ] Performance gates integrated into CI/CD
- [ ] Regression tests run on every model/config change
- [ ] Cost per 1M tokens tracked and within budget

---

## References

- vLLM Benchmarking: https://docs.vllm.ai/en/latest/performance_benchmark/benchmarks.html
- NVIDIA Nsight Systems: https://developer.nvidia.com/nsight-systems
- Kubernetes HPA: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- SLO Best Practices: https://sre.google/sre-book/service-level-objectives/
