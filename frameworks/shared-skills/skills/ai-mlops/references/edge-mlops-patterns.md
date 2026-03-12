# Edge MLOps & TinyML Patterns

Operational patterns for deploying ML models on edge devices, microcontrollers, and distributed IoT systems.

---

## Overview

**Edge MLOps** extends traditional MLOps practices to highly distributed deployments where models run on resource-constrained devices close to data sources. This includes:

- **TinyML**: ML on microcontrollers (kilobytes of memory)
- **Edge AI**: ML on edge devices (smartphones, gateways, embedded systems)
- **Federated Learning**: Distributed training without centralizing data

**Why Edge MLOps matters:**

- Latency requirements that cloud can't meet (<10ms inference)
- Privacy constraints (data must stay on-device)
- Bandwidth limitations (can't send all data to cloud)
- Offline operation requirements
- Cost optimization (reduce cloud inference costs)

**Market context:** IDC predicts 41.5+ billion IoT devices by 2025, generating 79.5+ zettabytes of data.

---

## Edge vs Cloud MLOps

| Aspect | Cloud MLOps | Edge MLOps |
|--------|-------------|------------|
| **Compute** | Unlimited | Severely constrained (KB-MB memory) |
| **Connectivity** | Always-on | Intermittent or offline |
| **Updates** | Immediate deployment | OTA with rollback complexity |
| **Monitoring** | Real-time dashboards | Batched telemetry |
| **Model size** | GB-scale acceptable | Must fit in KB-MB |
| **Latency** | 100ms-seconds | <10ms required |
| **Data** | Centralized | Distributed, often private |

---

## Core Edge MLOps Patterns

### Pattern 1: Device-Aware CI/CD

Traditional CI/CD pipelines assume homogeneous cloud targets. Edge MLOps requires device-specific builds and validation.

**Key components:**

- **Device matrix testing**: Test on representative hardware (different MCUs, edge devices)
- **Model quantization pipeline**: INT8, INT4, or binary quantization per device
- **Size gates**: Fail builds if model exceeds device memory
- **Power profiling**: Measure inference energy consumption

**Example pipeline:**

```yaml
# .github/workflows/edge-mlops.yml
jobs:
  build-and-test:
    strategy:
      matrix:
        device: [esp32, stm32, raspberry-pi-4, jetson-nano]
    steps:
      - name: Quantize model for device
        run: |
          python quantize.py \
            --model models/base.onnx \
            --target ${{ matrix.device }} \
            --output models/${{ matrix.device }}.tflite

      - name: Validate model size
        run: |
          MAX_SIZE=$(cat configs/${{ matrix.device }}.json | jq .max_model_kb)
          ACTUAL_SIZE=$(stat -f%z models/${{ matrix.device }}.tflite)
          if [ $ACTUAL_SIZE -gt $((MAX_SIZE * 1024)) ]; then
            echo "Model too large for ${{ matrix.device }}"
            exit 1
          fi

      - name: Run on-device tests
        run: |
          # Hardware-in-the-loop testing
          edge-impulse-cli test \
            --device ${{ matrix.device }} \
            --model models/${{ matrix.device }}.tflite
```

### Pattern 2: OTA Model Updates

Over-the-air updates for edge devices require careful orchestration to avoid bricking devices.

**Update workflow:**

1. **Staged rollout**: Update 1% → 10% → 50% → 100%
2. **Health checks**: Verify device stability after update
3. **Automatic rollback**: Revert if metrics degrade
4. **Differential updates**: Send only changed weights (reduce bandwidth)

**Rollback triggers:**

- Inference latency exceeds threshold
- Memory usage spikes
- Error rate increases
- Device stops reporting telemetry

**Example OTA configuration:**

```json
{
  "update_policy": {
    "rollout_stages": [
      {"percentage": 1, "duration_hours": 24, "pass_threshold": 0.99},
      {"percentage": 10, "duration_hours": 48, "pass_threshold": 0.98},
      {"percentage": 50, "duration_hours": 72, "pass_threshold": 0.97},
      {"percentage": 100, "duration_hours": null, "pass_threshold": 0.95}
    ],
    "rollback_triggers": {
      "error_rate_threshold": 0.05,
      "latency_p99_ms": 50,
      "memory_usage_percent": 90,
      "telemetry_silence_minutes": 30
    },
    "differential_updates": true,
    "compression": "lz4"
  }
}
```

### Pattern 3: Federated Learning Operations

Train models across distributed devices without centralizing raw data.

**Federated workflow:**

1. **Model distribution**: Push base model to devices
2. **Local training**: Each device trains on local data
3. **Gradient aggregation**: Collect and aggregate updates (FedAvg, FedProx)
4. **Privacy preservation**: Differential privacy, secure aggregation
5. **Model update**: Push aggregated model back to devices

**Key challenges:**

- **Non-IID data**: Device data distributions differ
- **Stragglers**: Some devices train slower
- **Communication efficiency**: Minimize gradient transfer
- **Privacy**: Prevent model inversion attacks

**Aggregation server example:**

```python
from typing import List, Dict
import numpy as np

class FederatedAggregator:
    def __init__(self, min_clients: int = 10, timeout_seconds: int = 300):
        self.min_clients = min_clients
        self.timeout = timeout_seconds
        self.client_updates: Dict[str, np.ndarray] = {}

    def receive_update(self, client_id: str, gradients: np.ndarray, n_samples: int):
        """Receive gradient update from a client device."""
        self.client_updates[client_id] = {
            'gradients': gradients,
            'n_samples': n_samples
        }

    def aggregate(self) -> np.ndarray:
        """FedAvg: Weighted average by sample count."""
        if len(self.client_updates) < self.min_clients:
            raise ValueError(f"Need {self.min_clients} clients, got {len(self.client_updates)}")

        total_samples = sum(u['n_samples'] for u in self.client_updates.values())
        aggregated = sum(
            u['gradients'] * (u['n_samples'] / total_samples)
            for u in self.client_updates.values()
        )
        return aggregated
```

### Pattern 4: Edge Drift Detection

Detect model drift without sending raw data to cloud.

**On-device metrics:**

- Prediction confidence distribution
- Input feature statistics (mean, variance)
- Inference latency trends
- Error rate (if labels available)

**Aggregated drift detection:**

```python
class EdgeDriftDetector:
    def __init__(self, baseline_stats: dict):
        self.baseline = baseline_stats

    def compute_device_stats(self, predictions: list) -> dict:
        """Compute local statistics on device."""
        confidences = [p['confidence'] for p in predictions]
        return {
            'mean_confidence': np.mean(confidences),
            'std_confidence': np.std(confidences),
            'low_confidence_rate': sum(1 for c in confidences if c < 0.7) / len(confidences)
        }

    def detect_drift(self, device_stats: dict) -> bool:
        """Compare device stats against baseline."""
        # PSI-like comparison for confidence distribution
        baseline_mean = self.baseline['mean_confidence']
        current_mean = device_stats['mean_confidence']

        drift_score = abs(current_mean - baseline_mean) / baseline_mean
        return drift_score > 0.1  # 10% shift triggers alert
```

### Pattern 5: Intermittent Connectivity Handling

Edge devices may operate offline for extended periods.

**Strategies:**

- **Local inference queue**: Buffer predictions during offline periods
- **Telemetry batching**: Aggregate metrics, send when connected
- **Model versioning**: Track which model version generated each prediction
- **Conflict resolution**: Handle stale model updates

**Offline-first architecture:**

```
Device (Offline-capable)
├── Local model store (multiple versions)
├── Inference engine
├── Prediction buffer (SQLite)
├── Telemetry aggregator
└── Sync manager
    ├── Check connectivity
    ├── Upload buffered telemetry
    ├── Download model updates
    └── Apply updates with rollback
```

---

## TinyML Specifics

### Memory Constraints

| Device Class | RAM | Flash | Example MCUs |
|--------------|-----|-------|--------------|
| Ultra-constrained | 2-64 KB | 32-256 KB | Cortex-M0, ESP8266 |
| Constrained | 64-512 KB | 256 KB-2 MB | Cortex-M4, ESP32 |
| Capable | 512 KB-4 MB | 2-16 MB | Cortex-M7, Jetson Nano |

### Model Optimization Techniques

**Quantization:**

- **INT8**: 4x smaller, minimal accuracy loss
- **INT4**: 8x smaller, some accuracy loss
- **Binary**: 32x smaller, significant accuracy loss

**Pruning:**

- Remove low-magnitude weights
- Structured pruning (remove entire channels)
- Iterative pruning with fine-tuning

**Knowledge distillation:**

- Train small "student" model to mimic large "teacher"
- Useful for compressing cloud models to edge

### TinyML Frameworks

| Framework | Supported Devices | Features |
|-----------|-------------------|----------|
| **TensorFlow Lite Micro** | Cortex-M, ESP32, Arduino | Google-backed, wide support |
| **Edge Impulse** | 50+ MCUs | End-to-end platform, AutoML |
| **CMSIS-NN** | ARM Cortex-M | Optimized kernels for ARM |
| **microTVM** | Various MCUs | Apache TVM for micro |

---

## Edge MLOps Platforms

| Platform | Type | Best For |
|----------|------|----------|
| **Edge Impulse** | SaaS | End-to-end TinyML development |
| **AWS IoT Greengrass** | Cloud | AWS ecosystem, Lambda at edge |
| **Azure IoT Edge** | Cloud | Azure ecosystem, container-based |
| **Google Cloud IoT** | Cloud | GCP ecosystem, TensorFlow focus |
| **Balena** | OSS/SaaS | Fleet management, Docker-based |

---

## Monitoring & Observability

### Batched Telemetry Pattern

Edge devices can't stream real-time metrics. Batch and send periodically.

```python
class EdgeTelemetryCollector:
    def __init__(self, batch_size: int = 100, flush_interval_seconds: int = 3600):
        self.batch_size = batch_size
        self.flush_interval = flush_interval_seconds
        self.buffer = []

    def record(self, metric_name: str, value: float, timestamp: float):
        self.buffer.append({
            'metric': metric_name,
            'value': value,
            'timestamp': timestamp,
            'device_id': self.device_id,
            'model_version': self.model_version
        })

        if len(self.buffer) >= self.batch_size:
            self.flush()

    def flush(self):
        if not self.buffer:
            return

        # Compress and send
        payload = gzip.compress(json.dumps(self.buffer).encode())
        try:
            requests.post(self.telemetry_endpoint, data=payload)
            self.buffer = []
        except requests.ConnectionError:
            # Keep buffer, retry later
            pass
```

### Key Metrics for Edge

- **Inference latency** (P50, P95, P99)
- **Memory usage** (peak, average)
- **Power consumption** (mW per inference)
- **Model version** (track which version produced each prediction)
- **Connectivity uptime** (% time connected)
- **Update success rate** (OTA reliability)

---

## Checklist: Edge MLOps Readiness

### Pre-Deployment

- [ ] Model fits within device memory constraints
- [ ] Quantization validated (accuracy vs size trade-off)
- [ ] Hardware-in-the-loop tests pass
- [ ] OTA update mechanism tested
- [ ] Rollback procedure validated
- [ ] Offline operation tested

### Production Monitoring

- [ ] Batched telemetry configured
- [ ] Drift detection thresholds set
- [ ] Fleet health dashboard created
- [ ] Alerting for device failures
- [ ] Model version tracking enabled

### Security

- [ ] Model encryption at rest
- [ ] Secure boot enabled
- [ ] OTA updates signed
- [ ] Telemetry encrypted in transit

---

## Related Resources

- [Deployment Patterns](deployment-patterns.md) - General deployment strategies
- [Drift Detection Guide](drift-detection-guide.md) - Drift detection techniques
- [Monitoring Best Practices](monitoring-best-practices.md) - Observability patterns
- [Multi-Region Patterns](multi-region-patterns.md) - Distributed deployments

---

## External References

- **Edge Impulse:** https://docs.edgeimpulse.com/
- **TensorFlow Lite Micro:** https://www.tensorflow.org/lite/microcontrollers
- **Federated Learning (Google):** https://federated.withgoogle.com/
- **AWS IoT Greengrass:** https://docs.aws.amazon.com/greengrass/
- **Azure IoT Edge:** https://docs.microsoft.com/azure/iot-edge/
