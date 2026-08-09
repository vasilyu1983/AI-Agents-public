# Chaos Tooling Recipes

Minimal, runnable recipes for the most common chaos and fault-injection tools. Each recipe shows the smallest working configuration and notes when to prefer it over alternatives.

All snippets assume a non-production environment unless explicitly noted. Always define a hypothesis, steady-state metric, and abort criteria before running any experiment.

---

## Table of Contents

- [Toxiproxy — Latency and Bandwidth Injection in Tests](#toxiproxy--latency-and-bandwidth-injection-in-tests)
- [AWS FIS — Account-Level Fault Injection](#aws-fis--account-level-fault-injection)
- [Azure Chaos Studio — Managed Fault Injection for Azure](#azure-chaos-studio--managed-fault-injection-for-azure)
- [Chaos Mesh — Kubernetes CRD-Based Faults](#chaos-mesh--kubernetes-crd-based-faults)
- [Litmus — Kubernetes GameDay Flows](#litmus--kubernetes-gameday-flows)
- [Gremlin — Commercial Fault Injection](#gremlin--commercial-fault-injection)
- [Gremlin Failure Flags — Application-Level Fault Injection](#gremlin-failure-flags--application-level-fault-injection)
- [Tool Selection Guide](#tool-selection-guide)

---

## Toxiproxy — Latency and Bandwidth Injection in Tests

**What it is:** A TCP proxy that sits between your service and a dependency during integration tests. You add "toxics" (fault rules) over its REST API. The service sees normal TCP but with injected latency, bandwidth caps, or dropped connections.

**When to use:** Unit and integration test suites where you want deterministic, repeatable fault injection without touching production infrastructure. Ideal for verifying timeout behavior, retry logic, and circuit-breaker thresholds in CI.

**Source:** https://github.com/Shopify/toxiproxy

### Docker Compose Setup

```yaml
# docker-compose.yml
services:
  toxiproxy:
    image: ghcr.io/shopify/toxiproxy:2.12.0
    ports:
      - "8474:8474"   # Toxiproxy REST API
      - "5433:5433"   # Proxied port for Postgres (example)
    command: ["--host", "0.0.0.0"]
```

### CLI: Create a Proxy and Inject Latency

```bash
# Install the toxiproxy-cli
brew install toxiproxy  # macOS
# or download from https://github.com/Shopify/toxiproxy/releases

# Create a proxy: local port 5433 → real Postgres on db:5432
toxiproxy-cli create postgres --listen localhost:5433 --upstream db:5432

# Add a 200ms latency toxic (both directions)
toxiproxy-cli toxic add postgres \
  --type latency \
  --attribute latency=200 \
  --attribute jitter=50

# List active toxics
toxiproxy-cli inspect postgres

# Remove the toxic after the test
toxiproxy-cli toxic delete postgres --toxicName latency_downstream
```

### CLI: Bandwidth Cap (slow network simulation)

```bash
# Cap bandwidth to 100 KB/s upstream (service → dependency)
toxiproxy-cli toxic add postgres \
  --type bandwidth \
  --stream upstream \
  --attribute rate=100
```

### REST API (language-agnostic, for test setup/teardown)

```bash
# Create proxy
curl -X POST http://localhost:8474/proxies \
  -H 'Content-Type: application/json' \
  -d '{"name":"redis","listen":"0.0.0.0:6380","upstream":"redis:6379","enabled":true}'

# Add connection reset toxic (simulates TCP RST)
curl -X POST http://localhost:8474/proxies/redis/toxics \
  -H 'Content-Type: application/json' \
  -d '{"type":"reset_peer","stream":"upstream","toxicity":1.0,"attributes":{"timeout":0}}'

# Remove all toxics (restore normal behavior)
curl -X DELETE http://localhost:8474/proxies/redis/toxics/reset_peer_upstream
```

---

## AWS FIS — Account-Level Fault Injection

**What it is:** AWS Fault Injection Service (FIS) is a managed chaos engineering service. Experiments run against real AWS resources (EC2, ECS, EKS, RDS, networking) inside your account using IAM-controlled actions and built-in stop conditions.

**When to use:** Validating resilience of AWS-hosted workloads in a staging or pre-production account. Use for scenarios that require real infrastructure faults: AZ failure simulation, RDS failover, EC2 termination, or latency injection in VPC traffic. Not suitable for local or CI use.

**Source:** https://docs.aws.amazon.com/fis/latest/userguide/what-is.html

### Minimal Experiment Template (YAML for AWS CLI)

```yaml
# fis-experiment-ec2-terminate.json
{
  "description": "Terminate 30% of EC2 instances in the web tier to validate auto-scaling",
  "targets": {
    "web-instances": {
      "resourceType": "aws:ec2:instance",
      "resourceTags": { "Tier": "web", "Env": "staging" },
      "selectionMode": "PERCENT(30)"
    }
  },
  "actions": {
    "terminate-web-instances": {
      "actionId": "aws:ec2:terminate-instances",
      "targets": { "Instances": "web-instances" }
    }
  },
  "stopConditions": [
    {
      "source": "aws:cloudwatch:alarm",
      "value": "arn:aws:cloudwatch:us-east-1:123456789012:alarm:HighErrorRate"
    }
  ],
  "roleArn": "arn:aws:iam::123456789012:role/FISExperimentRole",
  "tags": { "Owner": "sre-team", "Purpose": "resilience-gameday" }
}
```

### Run with AWS CLI

```bash
# Create the experiment template
aws fis create-experiment-template \
  --cli-input-json file://fis-experiment-ec2-terminate.json

# List templates to get the ID
aws fis list-experiment-templates --query 'experimentTemplates[*].id'

# Start an experiment
aws fis start-experiment --experiment-template-id EXT1234567890ABCDEF

# Monitor status
aws fis get-experiment --id EXP1234567890ABCDEF \
  --query 'experiment.state'
```

### Latency Injection on Network (VPC)

```bash
# Use the aws:network:latency action to inject latency into a subnet
aws fis create-experiment-template --cli-input-json '{
  "description": "Inject 100ms latency on subnet egress",
  "targets": {
    "staging-subnet": {
      "resourceType": "aws:ec2:subnet",
      "resourceArns": ["arn:aws:ec2:us-east-1:123456789012:subnet/subnet-abc123"]
    }
  },
  "actions": {
    "inject-latency": {
      "actionId": "aws:network:latency",
      "parameters": { "delayMilliseconds": "100", "jitterMilliseconds": "20" },
      "targets": { "Subnets": "staging-subnet" }
    }
  },
  "stopConditions": [{ "source": "none" }],
  "roleArn": "arn:aws:iam::123456789012:role/FISExperimentRole"
}'
```

### AZ Power Interruption Scenario (2024+)

FIS now supports a pre-built "AZ Availability: Power Interruption" scenario that triggers the expected symptoms of a complete AZ power loss: zonal EC2/EKS/ECS compute loss, RDS and ElastiCache failover, EBS unresponsiveness, and subnet connectivity loss. This scenario can also trigger Amazon ARC Zonal Autoshift to test automated AZ evacuation.

```bash
# Use the managed scenario; no custom template needed
aws fis start-experiment \
  --experiment-template-id EXT_AZ_POWER_INTERRUPTION \
  --experiment-options '{"actionsMode":"run-all"}' \
  --tags '{"Owner":"sre-team","AZ":"us-east-1a"}'
```

This is the highest-fidelity AZ-failure test available in AWS without involving AWS support. Use it in staging or with explicit runbook approval for production.

---

## Azure Chaos Studio — Managed Fault Injection for Azure

**What it is:** Microsoft's managed chaos engineering service for Azure workloads. The core experiment service (targets, capabilities, experiments against VMs, AKS, App Service, and other Azure resources) is generally available. **Verified as of 2026-07-11:** a newer **Chaos Studio Workspaces** capability — a scenario catalog with pre-built zone-failure and region-failure templates plus a drag-and-drop Scenario Designer — entered public preview on 2026-07-01; treat Workspaces-specific behavior and pricing as preview-stage and re-check `learn.microsoft.com/azure/chaos-studio` before relying on it for a production gate.

**When to use:** Validating resilience of Azure-hosted workloads, especially where you want a managed service with built-in blast-radius and stop-condition guardrails comparable to AWS FIS. Not suitable for local/CI use.

**Source:** https://learn.microsoft.com/en-us/azure/chaos-studio/chaos-studio-overview

### Minimal Experiment (ARM/Bicep-style JSON)

```json
{
  "properties": {
    "steps": [
      {
        "name": "Step1",
        "branches": [
          {
            "name": "Branch1",
            "actions": [
              {
                "type": "continuous",
                "name": "urn:csci:microsoft:virtualMachine:shutdown/1.0",
                "parameters": [{ "key": "abruptShutdown", "value": "true" }],
                "duration": "PT10M",
                "selectorId": "selector1"
              }
            ]
          }
        ]
      }
    ],
    "selectors": [
      {
        "id": "selector1",
        "type": "List",
        "targets": [
          { "type": "ChaosTarget", "id": "/subscriptions/<sub>/resourceGroups/staging-rg/providers/Microsoft.Compute/virtualMachines/vm1/providers/Microsoft.Chaos/targets/Microsoft-VirtualMachine" }
        ]
      }
    ]
  }
}
```

```bash
# Create the experiment, then start it
az rest --method put --url "/subscriptions/<sub>/resourceGroups/staging-rg/providers/Microsoft.Chaos/experiments/vm-shutdown-test?api-version=2024-01-01" --body @experiment.json

az rest --method post --url "/subscriptions/<sub>/resourceGroups/staging-rg/providers/Microsoft.Chaos/experiments/vm-shutdown-test/start?api-version=2024-01-01"
```

**Decision rule vs AWS FIS:** pick the managed chaos service that matches where the workload runs; the two are not interchangeable across clouds, and the experiment definition formats differ (JSON step/branch/action model here vs. targets/actions/stopConditions in FIS).

---

## Chaos Mesh — Kubernetes CRD-Based Faults

**What it is:** A CNCF project that manages chaos experiments as Kubernetes custom resources (CRDs). Faults are declared in YAML, scoped to namespaces or label selectors, and applied by a controller. Supports network faults, pod failures, stress (CPU/memory), I/O faults, and time skew.

**When to use:** Kubernetes clusters where you want GitOps-style chaos: experiments defined as YAML, versioned in source control, and applied with `kubectl`. Good for continuous chaos in staging and structured game days.

**Source:** https://chaos-mesh.org

### Install (Helm)

```bash
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm install chaos-mesh chaos-mesh/chaos-mesh \
  --namespace chaos-mesh --create-namespace \
  --set dashboard.create=true
```

### Network Latency Fault

```yaml
# network-delay.yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: add-latency-payment-service
  namespace: staging
spec:
  action: delay
  mode: all
  selector:
    namespaces:
      - staging
    labelSelectors:
      app: payment-service
  delay:
    latency: "200ms"
    jitter: "50ms"
    correlation: "25"
  duration: "5m"
```

```bash
kubectl apply -f network-delay.yaml
kubectl get networkchaos -n staging
kubectl delete -f network-delay.yaml  # stop the experiment
```

### Pod Kill Fault

```yaml
# pod-kill.yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: kill-one-worker
  namespace: staging
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces:
      - staging
    labelSelectors:
      app: worker
  gracePeriod: 0
```

```bash
kubectl apply -f pod-kill.yaml
```

---

## Litmus — Kubernetes GameDay Flows

**What it is:** A CNCF project focused on structured chaos workflows ("ChaosEngines" and "ChaosSchedules"). Litmus ships a hub of pre-built experiments (pod delete, network loss, node drain, disk fill) and a workflow engine for multi-step game days.

**When to use:** Teams that want pre-built, community-maintained experiment definitions without writing CRDs from scratch. Good for game-day orchestration across multiple fault types in sequence. The Litmus Hub provides AWS, GCP, Azure, and Kubernetes experiments.

**Source:** https://litmuschaos.io

### Install

Helm is the current recommended installation method (as of LitmusChaos 3.x; the legacy `kubectl apply` manifest approach is no longer maintained).

```bash
helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/
helm repo update
helm install chaos litmuschaos/litmus \
  --namespace litmus --create-namespace \
  --set portal.frontend.service.type=NodePort
# Verify
kubectl get pods -n litmus
```

### Minimal ChaosEngine: Pod Delete

LitmusChaos 3.x uses a namespaced ChaosEngine with the ChaosCenter UI or litmusctl CLI to manage experiments. The YAML structure below is the current v3 format.

```yaml
# pod-delete-engine.yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: pod-delete-test
  namespace: staging
spec:
  appinfo:
    appns: staging
    applabel: "app=api-server"
    appkind: deployment
  engineState: active
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "60"          # seconds
            - name: CHAOS_INTERVAL
              value: "10"          # kill one pod every 10s
            - name: FORCE
              value: "false"
```

```bash
kubectl apply -f pod-delete-engine.yaml

# Watch experiment progress
kubectl describe chaosengine pod-delete-test -n staging
kubectl get chaosresult pod-delete-test-pod-delete -n staging -o yaml
```

### GameDay Workflow (multi-step)

```yaml
# gameday-workflow.yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosSchedule
metadata:
  name: monthly-gameday
  namespace: staging
spec:
  schedule:
    repeat:
      properties:
        minChaosInterval: "720h"   # run once a month
  engineTemplateSpec:
    appinfo:
      appns: staging
      applabel: "app=checkout"
      appkind: deployment
    experiments:
      - name: pod-network-loss
        spec:
          components:
            env:
              - name: NETWORK_PACKET_LOSS_PERCENTAGE
                value: "100"
              - name: TOTAL_CHAOS_DURATION
                value: "120"
```

---

## Gremlin — Commercial Fault Injection

**What it is:** A commercial chaos engineering platform with a UI, RBAC, scenario library, and integrations for Kubernetes, VMs, containers, and cloud services. Gremlin Free Tier is available; full features require a subscription.

**When to use:** Teams that need a polished UI, approval workflows, and compliance-friendly audit logs for chaos experiments. Preferred for organizations where self-managed tooling (Chaos Mesh, Litmus) is not an option due to governance or support requirements.

**Source:** https://www.gremlin.com

### Install Gremlin Agent (Kubernetes)

```bash
helm repo add gremlin https://helm.gremlin.com
helm install gremlin gremlin/gremlin \
  --namespace gremlin --create-namespace \
  --set gremlin.secret.managed=true \
  --set gremlin.secret.type=secret \
  --set gremlin.secret.teamID="YOUR_TEAM_ID" \
  --set gremlin.secret.clusterID="staging-cluster" \
  --set gremlin.secret.teamSecret="YOUR_TEAM_SECRET"
```

### CLI: CPU Attack (container)

```bash
# Install gremlin CLI: https://www.gremlin.com/docs/installing-gremlin/
gremlin attack-container \
  --container-id $(docker ps -q --filter name=api-server) \
  cpu --cores 2 --length 60
```

### CLI: Network Latency on a Host

```bash
gremlin attack-host \
  --identifier staging-host-01 \
  network latency \
    --egress-ports 5432 \
    --delay 150 \
    --length 120
```

### Scenario via API (JSON)

```bash
curl -X POST https://api.gremlin.com/v1/scenarios \
  -H "Authorization: Key $GREMLIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DB Latency Scenario",
    "description": "Validate checkout survives 200ms DB latency",
    "hypothesis": "P95 checkout latency stays below 1s",
    "steps": [
      {
        "type": "delay",
        "args": { "length": 300 }
      },
      {
        "type": "attack",
        "args": {
          "command": {
            "type": "network",
            "commandType": "latency",
            "args": { "delay": 200, "length": 120, "egressPorts": ["5432"] }
          },
          "target": {
            "type": "Random",
            "hosts": { "tags": { "env": "staging" } },
            "percent": 25
          }
        }
      }
    ]
  }'
```

---

## Gremlin Failure Flags — Application-Level Fault Injection

**What it is:** Failure Flags injects faults at the application layer rather than at the network or infrastructure layer. You define named "failure flag" points in your code (or use a no-code sidecar proxy). When an experiment targets a flag, the SDK or proxy intercepts the call and applies the configured fault (latency, exception, status code change). Without an active experiment the flags are no-ops with no performance cost.

**When to use:** When Toxiproxy covers TCP but not higher-level logic (specific gRPC methods, internal function calls, SDK calls to AI providers). Also useful for teams that cannot modify infrastructure but can deploy a sidecar, or for injecting application-specific fault conditions (custom error types, partial responses).

**Source:** https://www.gremlin.com/docs/failure-flags-overview

### SDK-based (Go example)

```go
import failureflags "github.com/gremlin/failure-flags-go"

func chargePayment(ctx context.Context, amount int) (*ChargeResult, error) {
    // Declare a failure flag; no-ops when no experiment is active
    failureflags.Invoke(ctx, &failureflags.FailureFlag{
        Name: "payment-provider-call",
        Labels: map[string]string{"provider": "stripe"},
    })

    return stripe.Charge(ctx, amount)
}
```

### Sidecar Proxy (no code change required)

```yaml
# Add the Gremlin sidecar to your pod; it proxies the application's
# outbound traffic and applies faults based on active experiments.
# No SDK required -- configure fault injection points in the Gremlin UI.
containers:
  - name: app
    image: myapp:latest
  - name: gremlin-failure-flags-sidecar
    image: gremlin/failure-flags-sidecar:latest
    env:
      - name: GREMLIN_TEAM_ID
        valueFrom:
          secretKeyRef:
            name: gremlin-secret
            key: teamId
      - name: GREMLIN_TEAM_SECRET
        valueFrom:
          secretKeyRef:
            name: gremlin-secret
            key: teamSecret
      - name: GREMLIN_DEBUG
        value: "true"
```

**Decision rule:** Use the SDK when you need precise control over which code path is affected. Use the sidecar proxy when code changes are not feasible or when you want to add fault injection to a service without a deployment cycle.

---

## Tool Selection Guide

| Criterion | Toxiproxy | AWS FIS | Azure Chaos Studio | Chaos Mesh | Litmus | Gremlin / Failure Flags |
|-----------|-----------|---------|---------------------|------------|--------|-------------------------|
| Works in CI / local | Yes | No | No | No | No | Partially / Yes (no-op safe) |
| Kubernetes native | No | No | No (AKS via resource faults) | Yes | Yes | Yes (agent + sidecar) |
| Cloud infrastructure faults | No | Yes (AWS) | Yes (Azure) | No | Partial | Yes (multi-cloud) |
| Application-layer injection | No | No | No | No | No | Yes (Failure Flags) |
| Pre-built experiment library | No | Templates | Yes (Workspaces scenario catalog, preview) | No | Yes (Hub) | Yes |
| Commercial support / UI | No | AWS console | Azure portal | No | UI available | Yes |
| Cost | Free (OSS) | Pay per use | Pay per use (Workspaces preview free; GA pricing pending) | Free (OSS) | Free (OSS) | Free tier / paid |
| Best for | Deterministic TCP faults in CI | AWS production/staging | Azure production/staging | K8s GitOps chaos | K8s game days | Enterprise teams; app-layer faults |

**Verification note:** tool maturity and release cadence in this table were checked 2026-07-11. Chaos Mesh and LitmusChaos are both active CNCF Incubating projects (neither archived); Gremlin remains an independently operating company. Exact point-release numbers change frequently — verify the current release at each project's repository before pinning a version in a runbook or CI pipeline rather than trusting a cached number here.
