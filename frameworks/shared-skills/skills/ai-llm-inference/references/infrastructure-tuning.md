# Infrastructure Tuning for GPU-Heavy LLM Inference

Production-ready infrastructure optimization patterns for OS, containers, and Kubernetes environments running GPU-accelerated LLM inference workloads.

## OS & CPU Optimization

**NUMA Pinning & CPU Affinity**
- Pin GPU worker processes to NUMA nodes closest to PCIe root complex
- Use `numactl --cpunodebind=<node> --membind=<node>` for worker processes
- Avoid cross-NUMA memory access (2-3x latency penalty)

**Power Management**
- Disable unnecessary C-states: `cpupower frequency-set -g performance`
- Keep GPU persistence mode enabled: `nvidia-smi -pm 1`
- Prevent GPU frequency throttling with consistent power profiles

**Memory Configuration**
- Enable huge pages (2MB/1GB): improves TLB hit rates
  ```bash
  echo 1024 > /proc/sys/vm/nr_hugepages  # 2GB of 2MB pages
  ```
- Reserve huge pages at boot for predictable allocation
- Use `mlock()` for critical inference code paths

## GPU Driver & Runtime

**CUDA & Driver Compatibility**
- Match CUDA toolkit version to framework requirements
- Keep driver at recommended version (check framework docs)
- Test new drivers in staging before production rollout

**Multi-Process Service (MPS)**
- Enable when running multiple small concurrent workloads
- Improves GPU utilization for sub-saturating jobs
- Configure context limits based on memory constraints
  ```bash
  nvidia-cuda-mps-control -d  # Start MPS daemon
  export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps
  ```

**Multi-Instance GPU (MIG)**
- Use for GPU sharing with hardware isolation
- Configure MIG slices based on workload requirements
  ```bash
  nvidia-smi mig -cgi 9,9,9 -C  # Create 3x 1g.5gb instances
  ```
- Ideal for multi-tenant inference serving

## Container Optimization

**Image Optimization**
- Use slim base images (CUDA runtime, not devel)
- Minimize overlay FS layers (combine RUN commands)
- Pin CUDA compatibility layer version explicitly

**Storage Configuration**
- Avoid swap entirely: set `--memory-swap=0`
- Use `--shm-size` for IPC between processes
- Mount model cache on fast local NVMe (not network FS)

**Resource Limits**
```dockerfile
# Docker example
docker run \
  --gpus all \
  --shm-size=8g \
  --ulimit memlock=-1 \
  --ulimit stack=67108864 \
  --memory=32g \
  --cpuset-cpus="0-15" \
  your-llm-image
```

## Kubernetes Best Practices

**Topology-Aware Scheduling**
- Use node labels for GPU types: `nvidia.com/gpu.product=A100-SXM4-80GB`
- Enable topology manager for NUMA awareness
- Request NVLink-connected GPUs for multi-GPU jobs
  ```yaml
  resources:
    limits:
      nvidia.com/gpu: 2
  nodeSelector:
    nvidia.com/gpu.nvlink: "true"
  ```

**Resource Guarantees**
- Set `requests == limits` for QoS=Guaranteed
- Prevent CPU throttling with generous CPU requests
- Reserve GPU memory headroom (95% utilization target)

**Reduce Orchestration Jitter**
- Use `priorityClassName: system-cluster-critical`
- Set pod anti-affinity to avoid noisy neighbors
- Configure liveness/readiness probes with appropriate timeouts
  ```yaml
  livenessProbe:
    httpGet:
      path: /health
      port: 8080
    initialDelaySeconds: 120
    periodSeconds: 30
    timeoutSeconds: 10
  ```

**Local Storage for Cache/Spill**
- Prefer node-local NVMe over network storage
- Use `local-path-provisioner` or hostPath volumes
- Mount paths:
  - Model weights: `/var/lib/models` (read-only)
  - KV cache spill: `/var/lib/kv-cache` (read-write, fast)

## Networking Optimization

**RDMA Configuration**
- Enable RDMA for multi-node tensor parallel jobs
- Use RoCE v2 or InfiniBand where available
- Configure lossless networking (PFC/ECN)

**gRPC & HTTP Tuning**
- Set keepalive intervals: `grpc.keepalive_time_ms=10000`
- Enable HTTP/2 multiplexing for concurrent requests
- Tune connection pool sizes based on concurrency

**Bandwidth Provisioning**
- Ensure 10Gbps+ for KV cache offload paths
- Monitor network saturation (should stay <70%)
- Use jumbo frames (MTU=9000) for high-throughput workloads

## Validation Checklist

- [ ] NUMA topology verified: `numactl --hardware`
- [ ] GPU persistence mode enabled: `nvidia-smi -q -d PERFORMANCE`
- [ ] Huge pages allocated: `cat /proc/meminfo | grep Huge`
- [ ] Container overlay FS optimized (minimal layers)
- [ ] Kubernetes topology-aware scheduling configured
- [ ] Node-local NVMe mounted for cache/spill
- [ ] Network bandwidth tested: `iperf3` between nodes
- [ ] GPU health checks passing in pod readiness probes
- [ ] Resource requests/limits set for QoS=Guaranteed
- [ ] No swap enabled: `swapon -s` (should be empty)

## Common Issues

**Problem**: GPU underutilization despite workload
- Check: CPU bottleneck (use `nvidia-smi dmon` + `htop`)
- Check: Memory bandwidth saturation (`nvidia-smi dmon -s m`)
- Fix: Increase batch size or enable MPS

**Problem**: OOM despite sufficient GPU memory
- Check: KV cache size exceeding allocation
- Check: Memory fragmentation (`nvidia-smi --query-gpu=memory.free,memory.used`)
- Fix: Reduce max batch size or enable PagedAttention

**Problem**: High latency variance
- Check: CPU throttling (`cat /sys/fs/cgroup/cpu/cpu.stat`)
- Check: NUMA cross-socket access (`numastat`)
- Fix: Pin workers to NUMA nodes, set QoS=Guaranteed

## References

- NVIDIA GPU Best Practices: https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/
- Kubernetes Device Plugins: https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/device-plugins/
- NUMA Deep Dive: https://www.kernel.org/doc/html/latest/vm/numa.html
