```markdown
# Kubernetes Operations Template (DevOps)

*Purpose: A practical template for day-to-day Kubernetes operations: deploying apps, scaling, debugging, performing maintenance, and validating production readiness.*

---

# 1. Overview

**Cluster Name / Context:**  
[e.g., prod-eu1]

**Environment:**  
- [ ] dev  
- [ ] staging  
- [ ] prod  
- [ ] DR  

**Workload Type:**  
- [ ] Stateless app  
- [ ] Stateful app  
- [ ] CronJob  
- [ ] DaemonSet  
- [ ] Job  

**Change Type / Task:**  
- [ ] New deployment  
- [ ] Update deployment  
- [ ] Scale app  
- [ ] Debug incident  
- [ ] Node maintenance  
- [ ] Cluster upgrade  

---

# 2. Application Deployment

## 2.1 Deployment Manifest Skeleton

```

apiVersion: apps/v1
kind: Deployment
metadata:
  name: <app-name>
  labels:
    app: <app-name>
    env: <env>
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: <app-name>
  template:
    metadata:
      labels:
        app: <app-name>
        env: <env>
    spec:
      containers:
      - name: <app-name>
        image: <registry>/<image>:<tag>
        ports:
        - containerPort: 8080
        envFrom:
        - configMapRef:
            name: <app-config>
        - secretRef:
            name: <app-secret>
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "300m"
            memory: "256Mi"
        startupProbe:            # covers slow start; liveness and readiness wait until it passes
          httpGet:
            path: /healthz
            port: 8080
          periodSeconds: 5
          failureThreshold: <n>  # n x period = longest allowed start
        livenessProbe:           # process health only; no dependency checks
          httpGet:
            path: /healthz
            port: 8080
          periodSeconds: 10
        readinessProbe:          # can this pod serve traffic now
          httpGet:
            path: /ready
            port: 8080
          periodSeconds: 5

```

### Deployment Checklist

- [ ] Image pinned to digest or specific tag  
- [ ] Probes configured correctly  
- [ ] Resources set (requests/limits)  
- [ ] Config/Secret used (no inline secrets)  
- [ ] Labels and annotations set (tracing, version)  
- [ ] Rolling strategy defined  

Probe and rollout rules:
- Use a `startupProbe` for slow starts, not a long `initialDelaySeconds` on liveness. A fixed delay is a guess: too short restarts a pod that is still starting, too long hides a hung start.
- Keep `/healthz` (liveness) and `/ready` (readiness) separate. Liveness answers "is this process stuck?" and must not call the database or other shared dependencies, or one outage restarts every pod. Readiness may check what this pod needs to serve; decide whether a shared-dependency outage should drain every pod at once.
- During a rolling update, old and new versions serve together. The new version must accept the old version's requests, messages, and schema, and the old version must tolerate data the new one writes. Ship a breaking change in compatible steps (expand, migrate, contract) or use blue-green.

---

# 3. Service & Ingress

## 3.1 Service

```

apiVersion: v1
kind: Service
metadata:
  name: <app-name>
spec:
  type: ClusterIP
  selector:
    app: <app-name>
  ports:

- name: http
    port: 80
    targetPort: 8080

```

## 3.2 Ingress (Example)

```

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: <app-name>
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt
spec:
  tls:

- hosts: [ "<host>" ]
    secretName: <tls-secret>
  rules:
- host: <host>
    http:
      paths:
  - path: /
        pathType: Prefix
        backend:
          service:
            name: <app-name>
            port:
              number: 80

```

### Exposure Checklist

- [ ] Service type appropriate (ClusterIP/NodePort/LoadBalancer)  
- [ ] Ingress host configured  
- [ ] TLS via cert-manager or cloud LB  
- [ ] NetworkPolicy restricts traffic where needed  

---

# 4. Scaling & Autoscaling

## 4.1 Manual Scaling

```

kubectl scale deployment/<app> --replicas=5

```

Checklist:
- [ ] Scale tested in staging  
- [ ] Resources support replicas  
- [ ] HPA limits adjusted accordingly  

---

## 4.2 Horizontal Pod Autoscaler (HPA)

```

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: <app-name>
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: <app-name>
  minReplicas: 2
  maxReplicas: 10
  metrics:

- type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

```

HPA Checklist:
- [ ] Metrics server installed  
- [ ] Reasonable min/max  
- [ ] Target utilization based on real data  
- [ ] Avoid flapping (cooldown configured via HPA/tuning)  
- [ ] Every container in the target pod sets `resources.requests` for the scaled resource. CPU utilization is measured against the request, so a missing request leaves the HPA without a metric, and a request set far below real use makes it scale out early.  

---

# 5. Operational Debugging

## 5.1 Basic Commands

```

kubectl get pods -n <ns>
kubectl describe pod <pod> -n <ns>
kubectl logs <pod> -n <ns>
kubectl logs <pod> -n <ns> -c <container>
kubectl exec -it <pod> -n <ns> -- sh
kubectl get events -n <ns> --sort-by=.metadata.creationTimestamp

```

---

## 5.2 Common Issues & Checks

### CrashLoopBackOff

- [ ] Check `kubectl logs`  
- [ ] Check environment variables  
- [ ] Check config/secret mounts  
- [ ] Check liveness probe (too aggressive?)  
- [ ] Check image entrypoint  

---

### ImagePullBackOff

- [ ] Image name/tag correct  
- [ ] Registry credentials configured (imagePullSecrets)  
- [ ] Registry reachable  
- [ ] Rate limiting (DockerHub/others)  

---

### OOMKilled

- [ ] Check pod `status` and events  
- [ ] Increase memory requests/limits  
- [ ] Check memory leaks in app  
- [ ] Add limits gradually  

---

### Readiness/Liveness Failures

- [ ] Probe endpoints correct  
- [ ] Check app startup time  
- [ ] Increase `initialDelaySeconds`  
- [ ] Ensure dependency readiness (DB, cache)  

---

# 6. Node & Cluster Maintenance

## 6.1 Node Drain

```

kubectl cordon <node>
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data

```

After maintenance:
```

kubectl uncordon <node>

```

Checklist:
- [ ] PodDisruptionBudgets checked  
- [ ] Critical pods tolerated elsewhere  
- [ ] StatefulSets drained carefully  

---

## 6.2 Cluster Upgrade Checklist

- [ ] Control plane upgraded first  
- [ ] Node pools upgraded gradually  
- [ ] API deprecation checked (kubectl convert / kube-no-trouble)  
- [ ] Admission controllers tested  
- [ ] Backup of etcd / state taken  
- [ ] DR plan validated  

---

# 7. Resource Management

## 7.1 Baseline Resource Template

```

resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "300m"
    memory: "256Mi"

```

Checklist:
- [ ] Based on real usage (metrics)  
- [ ] Avoid no-limit pods  
- [ ] Avoid requests >> limits  
- [ ] Watch for throttling  

---

## 7.2 Monitoring & Alerts

Key metrics:
- Pod restarts  
- CrashLoopBackOff events  
- CPU/memory usage  
- API server latency  
- Node memory/disk pressure  

Checklist:
- [ ] Dashboards exist per service and per cluster  
- [ ] Alerts actionable and non-noisy  
- [ ] Logs enriched with pod/namespace labels  

---

# 8. Security & Policies

## 8.1 Pod Security

- [ ] Run as non-root  
- [ ] Read-only root filesystem when possible  
- [ ] Drop unnecessary capabilities  
- [ ] Restrict host networking/paths  

---

## 8.2 Network Policies

Example:
```

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app-to-db
spec:
  podSelector:
    matchLabels:
      app: app
  ingress:

- from:
  - podSelector:
        matchLabels:
          app: db
    ports:
  - protocol: TCP
      port: 5432

```

Checklist:
- [ ] Default deny policies considered  
- [ ] Access granted only where needed  

---

# 9. Rollout & Rollback

## 9.1 Check Rollout

```

kubectl rollout status deployment/<app> -n <ns>

```

## 9.2 Rollback Deployment

```

kubectl rollout undo deployment/<app> -n <ns>

```

Checklist:
- [ ] Changed image tagged  
- [ ] Rollback tested in non-prod  
- [ ] Monitoring in place post-rollout  

---

# 10. Final Operational Readiness Checklist

- [ ] Deployment manifest reviewed  
- [ ] Resource sizing acceptable  
- [ ] Probes validated  
- [ ] Secrets & configs wired via K8s objects  
- [ ] SLOs & alerts defined  
- [ ] Runbook linked  
- [ ] CI/CD integrated with cluster (no manual `kubectl` in prod)  

---

# END
```
