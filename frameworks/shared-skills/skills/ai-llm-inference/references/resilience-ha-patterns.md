# Resilience, High Availability & Traffic Management

Production patterns for building reliable LLM inference systems with uptime guarantees, safe rollouts, and overload protection.

## Overview

**Key requirements for production systems**:
- Multi-region/zone redundancy for high availability
- Safe deployment patterns (canary, blue-green, shadow)
- Overload protection and graceful degradation
- Traffic shaping and load shedding
- Stateful asset coordination (KV cache, model versions)

**Availability targets**:
- 99.9% = 43 minutes/month downtime
- 99.95% = 21 minutes/month downtime
- 99.99% = 4.3 minutes/month downtime

---

## Multi-Region & High Availability

### Active-Active Architecture

**Pattern**: Multiple regions serving traffic simultaneously

**Benefits**:
- Geographic load distribution
- Reduced latency (serve from nearest region)
- Graceful region failover

**Drawbacks**:
- Complex data synchronization
- Higher cost (duplicate infrastructure)
- Consistency challenges

**Configuration example (Kubernetes)**:
```yaml
# US-WEST region
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-inference-us-west
  labels:
    region: us-west
spec:
  replicas: 10
  template:
    spec:
      nodeSelector:
        region: us-west
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        resources:
          limits:
            nvidia.com/gpu: 1

---
# US-EAST region (identical config, different nodeSelector)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-inference-us-east
  labels:
    region: us-east
spec:
  replicas: 10
  template:
    spec:
      nodeSelector:
        region: us-east
      # ... rest identical
```

**Global load balancer** (GCP example):
```yaml
apiVersion: networking.gke.io/v1
kind: MultiClusterIngress
metadata:
  name: llm-global-ingress
spec:
  backends:
  - service: llm-inference-us-west
    healthCheck:
      path: /health
      port: 8080
  - service: llm-inference-us-east
    healthCheck:
      path: /health
      port: 8080
  routing:
    mode: geo  # Route to nearest region
```

### Active-Passive Architecture

**Pattern**: Primary region serves traffic, backup region on standby

**Benefits**:
- Simpler coordination
- Lower cost (standby uses fewer resources)
- Clear failover path

**Drawbacks**:
- Cold start latency on failover
- Higher latency during failover
- Wasted capacity in standby region

**Failover automation**:
```python
# Health check and failover script
import requests
import time

PRIMARY_ENDPOINT = "https://us-west.llm-api.com/health"
BACKUP_ENDPOINT = "https://us-east.llm-api.com/health"
DNS_UPDATE_API = "https://api.dns-provider.com/update"

def check_health(endpoint, timeout=5):
    try:
        response = requests.get(endpoint, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def failover_to_backup():
    # Update DNS to point to backup region
    requests.post(DNS_UPDATE_API, json={
        "record": "llm-api.com",
        "target": BACKUP_ENDPOINT
    })
    print("Failed over to backup region")

# Monitor loop
while True:
    if not check_health(PRIMARY_ENDPOINT):
        print("Primary region unhealthy")
        if check_health(BACKUP_ENDPOINT):
            failover_to_backup()
            break
        else:
            print("Backup also unhealthy! Manual intervention needed")

    time.sleep(10)  # Check every 10s
```

### Health Probes & Circuit Breakers

**Kubernetes liveness & readiness probes**:
```yaml
spec:
  containers:
  - name: vllm
    livenessProbe:
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 120  # Allow model loading
      periodSeconds: 30
      timeoutSeconds: 10
      failureThreshold: 3

    readinessProbe:
      httpGet:
        path: /ready  # Separate endpoint for readiness
        port: 8080
      initialDelaySeconds: 60
      periodSeconds: 10
      successThreshold: 1
      failureThreshold: 3
```

**Health check endpoint implementation**:
```python
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

app = FastAPI()

# Model warm status
model_loaded = False
last_successful_inference = time.time()

@app.get("/health")
async def health_check():
    """Liveness probe: Is process alive?"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy", "timestamp": time.time()}
    )

@app.get("/ready")
async def readiness_check():
    """Readiness probe: Can handle traffic?"""
    if not model_loaded:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "reason": "model_loading"}
        )

    # Check if recent inference succeeded (within 60s)
    if time.time() - last_successful_inference > 60:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "reason": "inference_failing"}
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ready", "model_loaded": True}
    )
```

**Circuit breaker pattern**:
```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e

    def on_success(self):
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
breaker = CircuitBreaker(failure_threshold=5, timeout=60)

def inference_request(prompt):
    return breaker.call(model.generate, prompt)
```

---

## Autoscaling Tied to SLOs

### SLO-Based Autoscaling

**Metrics for autoscaling**:
1. **P95 latency** - Scale up if latency degrading
2. **Queue depth** - Scale up if requests backing up
3. **GPU utilization** - Scale up if saturated

**HPA configuration**:
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
  # Primary metric: P95 latency
  - type: Pods
    pods:
      metric:
        name: inference_latency_p95_seconds
      target:
        type: AverageValue
        averageValue: "2.0"  # SLO: 2s P95

  # Secondary metric: Queue depth
  - type: Pods
    pods:
      metric:
        name: request_queue_depth
      target:
        type: AverageValue
        averageValue: "10"  # Max 10 queued per pod

  # Resource metric: GPU utilization
  - type: Resource
    resource:
      name: nvidia.com/gpu
      target:
        type: Utilization
        averageUtilization: 80  # Target 80% GPU util

  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100  # Double replicas if needed
        periodSeconds: 60
      - type: Pods
        value: 4  # Or add 4 pods
        periodSeconds: 60
      selectPolicy: Max  # Pick more aggressive policy

    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5min before scale down
      policies:
      - type: Percent
        value: 25  # Reduce by 25% max
        periodSeconds: 60
      selectPolicy: Min  # Pick more conservative policy
```

### Pre-warming Replicas

**Problem**: Cold start latency when scaling up

**Solution**: Keep warm standby replicas

**Implementation**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-inference-warm-pool
spec:
  replicas: 5  # Always-warm pool
  template:
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        lifecycle:
          postStart:
            exec:
              command:
              - /bin/sh
              - -c
              - |
                # Send dummy requests to warm up model
                sleep 30
                curl -X POST http://localhost:8080/v1/completions \
                  -d '{"model": "...", "prompt": "Hello", "max_tokens": 1}'
```

**Pre-warming script**:
```python
import requests
import time

def prewarm_replica(endpoint, num_warmup_requests=10):
    """Send dummy requests to warm up CUDA kernels and caches"""
    for i in range(num_warmup_requests):
        try:
            requests.post(
                f"{endpoint}/v1/completions",
                json={
                    "model": "meta-llama/Llama-2-13b-hf",
                    "prompt": f"Warmup request {i}",
                    "max_tokens": 1
                },
                timeout=30
            )
            time.sleep(1)
        except Exception as e:
            print(f"Warmup {i} failed: {e}")

    print("Replica warmed and ready")
```

### Block Deploys When SLOs Regress

**Pre-deployment validation**:
```yaml
# GitLab CI example
stages:
  - build
  - benchmark
  - deploy

benchmark:
  stage: benchmark
  script:
    - python benchmarks/benchmark.py --output results.json
    - python scripts/validate_slo.py --results results.json --slo slo.yaml
  artifacts:
    reports:
      junit: benchmark_results.xml
  only:
    - main

deploy:
  stage: deploy
  script:
    - kubectl apply -f k8s/
  dependencies:
    - benchmark  # Only deploy if benchmark passed
  only:
    - main
```

**SLO validation script**:
```python
# scripts/validate_slo.py
import json
import yaml
import sys

def validate_slo(results_file, slo_file):
    with open(results_file) as f:
        results = json.load(f)

    with open(slo_file) as f:
        slo = yaml.safe_load(f)

    violations = []

    # Check latency SLO
    if results['latency_p95'] > slo['latency']['p95_seconds']:
        violations.append(
            f"P95 latency {results['latency_p95']:.2f}s exceeds SLO {slo['latency']['p95_seconds']}s"
        )

    # Check throughput SLO
    if results['throughput_qps'] < slo['throughput']['min_qps']:
        violations.append(
            f"Throughput {results['throughput_qps']:.0f} QPS below SLO {slo['throughput']['min_qps']} QPS"
        )

    # Check cost SLO
    if results['cost_per_1m_tokens'] > slo['cost']['max_per_1m_tokens']:
        violations.append(
            f"Cost ${results['cost_per_1m_tokens']:.2f}/1M exceeds SLO ${slo['cost']['max_per_1m_tokens']:.2f}/1M"
        )

    if violations:
        print("[FAIL] SLO violations detected - blocking deployment:")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)
    else:
        print("[OK] All SLOs met - proceeding with deployment")
        sys.exit(0)
```

---

## Overload Protection & Backpressure

### Token-Level Rate Limiting

**Prevent abuse and control costs**:
```python
from fastapi import FastAPI, HTTPException
from collections import defaultdict
import time

app = FastAPI()

# Token budget per user (tokens/minute)
TOKEN_BUDGET = 10000
user_tokens = defaultdict(lambda: {'count': 0, 'reset_time': time.time()})

@app.post("/v1/completions")
async def generate(request: dict, user_id: str):
    # Reset budget if window expired
    now = time.time()
    if now - user_tokens[user_id]['reset_time'] > 60:
        user_tokens[user_id] = {'count': 0, 'reset_time': now}

    # Check budget
    if user_tokens[user_id]['count'] >= TOKEN_BUDGET:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {60 - (now - user_tokens[user_id]['reset_time']):.0f}s"
        )

    # Process request
    output = await model.generate(request['prompt'], max_tokens=request.get('max_tokens', 256))

    # Deduct tokens
    tokens_used = len(output.split())
    user_tokens[user_id]['count'] += tokens_used

    return {"text": output, "tokens_used": tokens_used}
```

### Queue Caps & Request Shedding

**Prevent queue buildup**:
```python
from asyncio import Queue
from fastapi import FastAPI, HTTPException

app = FastAPI()
request_queue = Queue(maxsize=100)  # Max 100 queued requests

@app.post("/v1/completions")
async def generate(request: dict):
    # Check queue capacity
    if request_queue.full():
        raise HTTPException(
            status_code=503,
            detail="Server overloaded. Please retry later."
        )

    # Enqueue request
    await request_queue.put(request)

    # Wait for processing
    result = await process_request(request)
    return result
```

### Graceful Degradation

**Fallback strategies**:

1. **Shorter max_tokens**:
```python
def adaptive_max_tokens(queue_depth, baseline=256):
    """Reduce max_tokens when system overloaded"""
    if queue_depth > 50:
        return baseline // 4  # 64 tokens
    elif queue_depth > 20:
        return baseline // 2  # 128 tokens
    else:
        return baseline  # 256 tokens
```

2. **Cached responses**:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_generate(prompt: str):
    """Return cached response if available"""
    return model.generate(prompt)

def generate_with_fallback(prompt: str):
    try:
        # Try cached first
        return cached_generate(prompt)
    except:
        # Fall back to real generation
        return model.generate(prompt)
```

3. **Smaller model fallback**:
```python
PRIMARY_MODEL = "llama-70b"
FALLBACK_MODEL = "llama-13b"

def generate_with_fallback(prompt: str, queue_depth: int):
    if queue_depth > 30:
        # Use smaller, faster model when overloaded
        return small_model.generate(prompt)
    else:
        return large_model.generate(prompt)
```

### Priority-Based Load Shedding

**Shed low-priority traffic first**:
```python
from enum import Enum

class Priority(Enum):
    CRITICAL = 0  # Always serve
    HIGH = 1
    MEDIUM = 2
    LOW = 3  # Shed first

@app.post("/v1/completions")
async def generate(request: dict, priority: Priority = Priority.MEDIUM):
    queue_depth = request_queue.qsize()

    # Shed low-priority requests when overloaded
    if queue_depth > 50 and priority == Priority.LOW:
        raise HTTPException(
            status_code=503,
            detail="Low-priority request rejected due to high load"
        )

    if queue_depth > 80 and priority == Priority.MEDIUM:
        raise HTTPException(
            status_code=503,
            detail="Medium-priority request rejected due to high load"
        )

    # Only CRITICAL and HIGH requests make it here when queue > 80

    return await process_request(request)
```

---

## Traffic Shaping & Safe Rollouts

### Canary Deployments

**Pattern**: Route small % of traffic to new version, monitor, then increase

**Kubernetes canary setup**:
```yaml
# Stable deployment (90% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-stable
  labels:
    version: stable
spec:
  replicas: 9
  template:
    metadata:
      labels:
        app: llm-inference
        version: stable

---
# Canary deployment (10% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-canary
  labels:
    version: canary
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: llm-inference
        version: canary
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:v0.3.0  # New version

---
# Service routes to both
apiVersion: v1
kind: Service
metadata:
  name: llm-inference
spec:
  selector:
    app: llm-inference  # Selects both stable + canary
  ports:
  - port: 8080
```

**Progressive rollout**:
```bash
# Start: 10% canary
kubectl scale deployment llm-canary --replicas=1
kubectl scale deployment llm-stable --replicas=9

# Monitor metrics for 30 minutes

# If healthy: 50% canary
kubectl scale deployment llm-canary --replicas=5
kubectl scale deployment llm-stable --replicas=5

# Monitor for 30 minutes

# If healthy: 100% canary
kubectl scale deployment llm-canary --replicas=10
kubectl scale deployment llm-stable --replicas=0

# If unhealthy: Rollback
kubectl scale deployment llm-canary --replicas=0
kubectl scale deployment llm-stable --replicas=10
```

**Automated canary with Flagger**:
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: llm-inference
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-inference
  service:
    port: 8080
  analysis:
    interval: 1m
    threshold: 5  # Number of checks before promotion
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99  # Require 99% success rate
    - name: latency-p95
      thresholdRange:
        max: 2000  # Max 2s P95 latency
  canaryAnalysis:
    stepWeight: 10  # Increase traffic by 10% each step
    maxWeight: 50  # Max 50% canary traffic
```

### Shadow Traffic

**Pattern**: Send traffic to new version without returning responses to users

**Benefits**:
- Zero user impact
- Real production load testing
- Compare response quality

**Implementation**:
```python
import asyncio
import requests

PRIMARY_ENDPOINT = "http://llm-stable:8080"
SHADOW_ENDPOINT = "http://llm-canary:8080"

async def dual_request(prompt: str):
    # Send to both endpoints
    primary_task = asyncio.create_task(
        requests.post(PRIMARY_ENDPOINT, json={"prompt": prompt})
    )

    shadow_task = asyncio.create_task(
        requests.post(SHADOW_ENDPOINT, json={"prompt": prompt})
    )

    # Wait for primary
    primary_response = await primary_task

    # Log shadow response (async, don't block)
    asyncio.create_task(log_shadow_response(shadow_task))

    # Return only primary response to user
    return primary_response

async def log_shadow_response(task):
    try:
        shadow_response = await task
        # Log for comparison
        print(f"Shadow response: {shadow_response.json()}")
    except Exception as e:
        print(f"Shadow request failed: {e}")
```

### Weighted Routing

**Route traffic based on confidence**:
```python
import random

def weighted_route(prompt: str, stable_weight=0.9, canary_weight=0.1):
    """Route to stable or canary based on weights"""
    rand = random.random()

    if rand < canary_weight:
        return canary_model.generate(prompt)
    else:
        return stable_model.generate(prompt)
```

**Abort thresholds**:
```python
canary_error_count = 0
canary_total_requests = 0

def route_with_abort(prompt: str):
    global canary_error_count, canary_total_requests

    # Check abort threshold
    if canary_total_requests > 100:
        error_rate = canary_error_count / canary_total_requests
        if error_rate > 0.05:  # >5% error rate
            print("Canary error rate too high - aborting rollout")
            return stable_model.generate(prompt)  # Fallback to stable

    # Route to canary (weighted)
    canary_total_requests += 1
    try:
        return canary_model.generate(prompt)
    except Exception as e:
        canary_error_count += 1
        raise e
```

### Sticky Sessions (KV Cache Reuse)

**When needed**: Multi-turn conversations with KV cache reuse

**Implementation**:
```yaml
# Kubernetes service with session affinity
apiVersion: v1
kind: Service
metadata:
  name: llm-inference
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600  # 1 hour session
  selector:
    app: llm-inference
  ports:
  - port: 8080
```

**Application-level session routing**:
```python
from fastapi import FastAPI, Cookie

app = FastAPI()

# Map session ID to replica
session_replicas = {}

@app.post("/v1/chat")
async def chat(
    message: str,
    session_id: str = Cookie(None)
):
    # Route to same replica for session
    if session_id in session_replicas:
        replica = session_replicas[session_id]
    else:
        replica = select_replica()  # Round-robin
        session_replicas[session_id] = replica

    # Forward to replica with KV cache
    return replica.generate(message, session_id=session_id)
```

---

## Stateful Asset Coordination

### KV Cache Invalidation

**Problem**: Cached keys/values become stale after model update

**Solution**: Coordinate cache invalidation with rollout

```python
import redis

cache = redis.Redis(host='localhost', port=6379)

def invalidate_kv_cache(deployment_id: str):
    """Clear all KV cache entries for deployment"""
    pattern = f"kv_cache:{deployment_id}:*"
    keys = cache.keys(pattern)
    if keys:
        cache.delete(*keys)
        print(f"Invalidated {len(keys)} KV cache entries")

# Call during deployment
invalidate_kv_cache("llm-inference-v2")
```

### Prompt & Index Version Pinning

**Ensure consistent prompt templates across replicas**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prompt-templates-v2
data:
  system_prompt: "You are a helpful assistant..."
  user_template: "<user>{message}</user>"
  assistant_template: "<assistant>{response}</assistant>"

---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: vllm
        env:
        - name: PROMPT_VERSION
          value: "v2"
        volumeMounts:
        - name: prompts
          mountPath: /prompts
      volumes:
      - name: prompts
        configMap:
          name: prompt-templates-v2
```

### Atomic Rollout/Rollback

**Blue-Green deployment**:
```bash
# Deploy green (new version)
kubectl apply -f deployment-green.yaml

# Wait for health checks
kubectl wait --for=condition=available deployment/llm-green

# Switch traffic (instant cutover)
kubectl patch service llm-inference -p '{"spec":{"selector":{"version":"green"}}}'

# Rollback if needed
kubectl patch service llm-inference -p '{"spec":{"selector":{"version":"blue"}}}'
```

---

## Checklist: High Availability Ready

- [ ] Region/zone failover tested (simulate zone outage)
- [ ] Health checks + circuit breakers configured and tested
- [ ] Autoscale policies based on latency + queue depth + GPU util
- [ ] Pre-warm replicas configured (reduce cold start)
- [ ] Overload fallbacks defined (rate limits, queue caps, smaller model)
- [ ] Canary deployment tested (10% → 50% → 100%)
- [ ] Shadow traffic tested (validate new version quality)
- [ ] Abort gates configured (rollback if error rate > 5%)
- [ ] Rollout artifacts versioned (model, prompts, KV cache, adapters)
- [ ] KV cache invalidation coordinated with deployments
- [ ] Sticky sessions configured (if KV cache reuse needed)
- [ ] SLO validation blocks bad deployments

---

## References

- Google SRE Book: https://sre.google/sre-book/table-of-contents/
- Kubernetes HPA: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- Flagger (Progressive Delivery): https://flagger.app/
- Circuit Breaker Pattern: https://microservices.io/patterns/reliability/circuit-breaker.html
