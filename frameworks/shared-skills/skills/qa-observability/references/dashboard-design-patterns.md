# Dashboard Design Patterns

Dashboard hierarchy, layout patterns, and design principles for effective observability. Reduce mean-time-to-diagnosis by building dashboards people actually use.

## Contents

- [Dashboard Layers](#dashboard-layers)
- [Golden Signals Dashboard](#golden-signals-dashboard)
- [USE Method Dashboards](#use-method-dashboards)
- [RED Method Dashboards](#red-method-dashboards)
- [Layout Anti-Patterns](#layout-anti-patterns)
- [Grafana Dashboard-as-Code](#grafana-dashboard-as-code)
- [Dashboard Naming Conventions](#dashboard-naming-conventions)
- [Variable Templates](#variable-templates)
- [Refresh Intervals and Time Ranges](#refresh-intervals-and-time-ranges)
- [Annotation Overlays](#annotation-overlays)
- [Related Resources](#related-resources)

---

## Dashboard Layers

Organize dashboards in a hierarchy. Each layer serves a different audience and use case.

### Three-Layer Model

```
Layer 1: Executive / Fleet Overview
  - One dashboard for all services
  - SLO status, error budgets, overall health
  - Audience: engineering leadership, incident commanders

Layer 2: Service Overview
  - One dashboard per service
  - Golden signals, dependencies, recent deploys
  - Audience: on-call engineers, service owners

Layer 3: Component / Debug
  - Detailed dashboards per component
  - Database queries, cache hit rates, queue depths
  - Audience: engineers debugging specific issues
```

### Layer Details

| Layer | Dashboard Count | Update Frequency | Time Range Default | Key Panels |
|-------|----------------|------------------|--------------------|------------|
| **Executive** | 1-3 total | Hourly or daily | 7d / 30d | SLO status, error budget, incident count |
| **Service** | 1 per service | Every 30s-1m | 1h / 6h | Latency, errors, traffic, saturation |
| **Component** | 1-5 per service | Every 10-30s | 15m / 1h | DB queries, cache, queues, threads, GC |

### Navigation Pattern

```
Fleet Overview
├── Order Service
│   ├── Order API (component)
│   ├── Order Database (component)
│   └── Order Worker (component)
├── Payment Service
│   ├── Payment API (component)
│   └── Payment Gateway (component)
└── Auth Service
    ├── Auth API (component)
    └── Token Store (component)
```

Implement navigation using Grafana links or dashboard variables that drill down from fleet to service to component.

---

## Golden Signals Dashboard

The four golden signals (from Google SRE) form the foundation of every service dashboard.

### Dashboard Layout

```
+-----------------------------------------------------------+
| SERVICE: Order API                      [env] [timerange]  |
+-----------------------------------------------------------+
| Latency (P50, P95, P99)  | Error Rate (%)                 |
|  [timeseries graph]       |  [timeseries graph]            |
|  Target: P99 < 500ms     |  Target: < 0.1%                |
+---------------------------+--------------------------------+
| Traffic (req/s)           | Saturation (CPU, Mem, Conns)   |
|  [timeseries graph]       |  [timeseries graph]            |
|  Compared to last week   |  Threshold lines at 80%        |
+---------------------------+--------------------------------+
| Recent Deployments        | Active Alerts                  |
|  [annotation list]        |  [alert list panel]            |
+---------------------------+--------------------------------+
```

### PromQL Queries

```promql
# Latency - P50, P95, P99
histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket{service="order-api"}[5m])) by (le))
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service="order-api"}[5m])) by (le))
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{service="order-api"}[5m])) by (le))

# Error Rate
sum(rate(http_requests_total{service="order-api", status=~"5.."}[5m]))
/
sum(rate(http_requests_total{service="order-api"}[5m]))

# Traffic
sum(rate(http_requests_total{service="order-api"}[5m]))

# Saturation - CPU
rate(container_cpu_usage_seconds_total{pod=~"order-api-.*"}[5m])
/
container_spec_cpu_quota{pod=~"order-api-.*"} * 1e-5

# Saturation - Memory
container_memory_working_set_bytes{pod=~"order-api-.*"}
/
container_spec_memory_limit_bytes{pod=~"order-api-.*"}
```

---

## USE Method Dashboards

USE (Utilization, Saturation, Errors) is best for infrastructure and resource-oriented components.

### When to Use USE

- Database servers
- Load balancers
- Message queues
- Network interfaces
- Storage systems

### USE Dashboard Template

| Resource | Utilization | Saturation | Errors |
|----------|-------------|------------|--------|
| **CPU** | % busy time | Run queue length | Machine check exceptions |
| **Memory** | % used | Swap usage, OOM events | Allocation failures |
| **Disk** | % capacity used | I/O queue depth | Read/write errors |
| **Network** | % bandwidth used | Packet queue drops | CRC errors, timeouts |
| **Database** | Connection pool % used | Wait queue length | Query errors, deadlocks |

### PromQL for USE Panels

```promql
# CPU Utilization
1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance)

# CPU Saturation (load average vs CPU count)
node_load1 / count(node_cpu_seconds_total{mode="idle"}) by (instance)

# Memory Utilization
1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)

# Memory Saturation (swap usage)
node_memory_SwapTotal_bytes - node_memory_SwapFree_bytes

# Disk Utilization
1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)

# Disk Saturation (I/O queue depth)
rate(node_disk_io_time_weighted_seconds_total[5m])

# Network Utilization
rate(node_network_receive_bytes_total[5m]) * 8 / 1e9  # Gbps

# Network Errors
rate(node_network_receive_errs_total[5m])
+ rate(node_network_transmit_errs_total[5m])
```

---

## RED Method Dashboards

RED (Rate, Errors, Duration) is best for request-driven services (APIs, microservices).

### When to Use RED

- API gateways
- Microservice endpoints
- GraphQL resolvers
- gRPC services
- Background job processors

### RED Dashboard Layout

```
+-----------------------------------------------------------+
| SERVICE: Payment API          [env] [endpoint] [timerange] |
+-----------------------------------------------------------+
| Rate (requests/sec by endpoint)                            |
|  [stacked area chart]                                      |
|  Breakdown: /charge, /refund, /status, /webhook            |
+-----------------------------------------------------------+
| Errors (error rate % by endpoint)                          |
|  [timeseries with threshold line]                          |
|  Breakdown: 4xx vs 5xx                                     |
+-----------------------------------------------------------+
| Duration (P50, P95, P99 by endpoint)                       |
|  [heatmap or timeseries]                                   |
|  Color coding: green < 200ms, yellow < 500ms, red > 500ms |
+-----------------------------------------------------------+
| Top Errors (by message)    | Slowest Endpoints             |
|  [table: error, count]     |  [table: endpoint, P99]       |
+---------------------------+--------------------------------+
```

### PromQL for RED Panels

```promql
# Rate: requests per second by endpoint
sum(rate(http_requests_total{service="payment-api"}[5m])) by (handler)

# Errors: error rate by type
sum(rate(http_requests_total{service="payment-api", status=~"4.."}[5m])) by (handler)  # 4xx
sum(rate(http_requests_total{service="payment-api", status=~"5.."}[5m])) by (handler)  # 5xx

# Duration: latency heatmap
sum(rate(http_request_duration_seconds_bucket{service="payment-api"}[5m])) by (le, handler)

# Duration: P99 per endpoint
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{service="payment-api"}[5m]))
  by (le, handler)
)
```

---

## Layout Anti-Patterns

### Common Mistakes

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| **Wall of graphs** | 30+ panels, no visual hierarchy | Group into rows, limit to 8-12 panels |
| **No context** | Graphs with no labels, thresholds, or targets | Add panel descriptions, threshold lines |
| **Wrong chart type** | Using line charts for categorical data | Use bar charts for comparisons, tables for lists |
| **Missing time correlation** | Panels use different time ranges | Sync all panels to dashboard time picker |
| **No drill-down links** | Dead-end dashboards | Add links from overview to detail dashboards |
| **Stale dashboards** | Dashboards for services that no longer exist | Quarterly audit, delete or archive |
| **Everyone's dashboard** | One dashboard serves all audiences | Split into layers (executive, service, component) |
| **Alert-only dashboard** | No context around alert state | Show trends, not just current state |

### Good Layout Principles

1. **Top-to-bottom priority** -- most important panels at the top
2. **Left-to-right flow** -- related panels side by side for comparison
3. **Consistent sizing** -- use Grafana row height standards (8 or 12 units)
4. **Threshold lines** -- every metric panel has a target or threshold line
5. **Empty state guidance** -- "No data" states explain what is expected
6. **Color consistency** -- green = good, yellow = warning, red = critical across all dashboards

### Panel Count Guidelines

| Dashboard Type | Max Panels | Rows |
|---------------|-----------|------|
| Executive overview | 6-8 | 2-3 |
| Service overview | 8-12 | 3-4 |
| Component detail | 12-16 | 4-6 |
| Debugging / ad-hoc | No limit | As needed, collapse rows |

---

## Grafana Dashboard-as-Code

### JSON Provisioning

Store dashboards in Git, deploy via Grafana provisioning.

```json
{
  "dashboard": {
    "uid": "order-service-overview",
    "title": "Order Service Overview",
    "tags": ["service", "order", "slo"],
    "timezone": "utc",
    "refresh": "30s",
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "templating": {
      "list": [
        {
          "name": "environment",
          "type": "query",
          "query": "label_values(http_requests_total{service=\"order-service\"}, environment)",
          "current": { "text": "production", "value": "production" },
          "refresh": 2
        }
      ]
    },
    "panels": [
      {
        "title": "Request Rate",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{service=\"order-service\", environment=\"$environment\"}[5m]))",
            "legendFormat": "req/s"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "custom": {
              "lineWidth": 2,
              "fillOpacity": 10
            },
            "unit": "reqps"
          }
        }
      },
      {
        "title": "Error Rate",
        "type": "timeseries",
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 },
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{service=\"order-service\", environment=\"$environment\", status=~\"5..\"}[5m])) / sum(rate(http_requests_total{service=\"order-service\", environment=\"$environment\"}[5m]))",
            "legendFormat": "error rate"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percentunit",
            "thresholds": {
              "steps": [
                { "value": 0, "color": "green" },
                { "value": 0.01, "color": "yellow" },
                { "value": 0.05, "color": "red" }
              ]
            }
          }
        }
      }
    ]
  }
}
```

### Provisioning Directory Structure

```
grafana/
  provisioning/
    dashboards/
      default.yaml              # Provisioning config
    dashboard-files/
      executive/
        fleet-overview.json
      services/
        order-service.json
        payment-service.json
      components/
        order-database.json
        order-cache.json
```

### Provisioning Config

```yaml
# grafana/provisioning/dashboards/default.yaml
apiVersion: 1

providers:
  - name: "default"
    orgId: 1
    folder: ""
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

### Grafonnet (Jsonnet Library)

```jsonnet
// order-service.jsonnet
local grafana = import 'grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local prometheus = grafana.prometheus;
local graphPanel = grafana.graphPanel;
local template = grafana.template;

dashboard.new(
  'Order Service Overview',
  uid='order-service-overview',
  tags=['service', 'order'],
  time_from='now-1h',
  refresh='30s',
)
.addTemplate(
  template.datasource('datasource', 'prometheus', 'Prometheus')
)
.addTemplate(
  template.new('environment', '$datasource', 'label_values(http_requests_total{service="order-service"}, environment)')
)
.addPanel(
  graphPanel.new(
    'Request Rate',
    datasource='$datasource',
    format='reqps',
    span=6,
  ).addTarget(
    prometheus.target(
      'sum(rate(http_requests_total{service="order-service", environment="$environment"}[5m]))',
      legendFormat='req/s',
    )
  ),
  gridPos={x: 0, y: 0, w: 12, h: 8},
)
```

---

## Dashboard Naming Conventions

### Naming Pattern

```
[Layer] - [Service/Team] - [Aspect]

Examples:
  Fleet - All Services - SLO Overview
  Service - Order API - Golden Signals
  Service - Payment API - RED Metrics
  Component - Order DB - Connection Pool
  Debug - Order API - Request Tracing
```

### Tagging Strategy

| Tag | Purpose | Examples |
|-----|---------|---------|
| `layer:executive` | Dashboard hierarchy | executive, service, component |
| `service:order-api` | Service ownership | order-api, payment-api |
| `team:commerce` | Team ownership | commerce, platform, infra |
| `method:red` | Methodology | red, use, golden-signals, slo |
| `stack:kubernetes` | Technology | kubernetes, postgresql, redis |

---

## Variable Templates

Dashboard variables make dashboards reusable across environments, services, and time ranges.

### Essential Variables

```yaml
variables:
  - name: environment
    label: Environment
    query: "label_values(up, environment)"
    type: query
    default: production

  - name: service
    label: Service
    query: "label_values(http_requests_total{environment='$environment'}, service)"
    type: query
    multi: true

  - name: namespace
    label: Namespace
    query: "label_values(kube_pod_info{cluster='$cluster'}, namespace)"
    type: query

  - name: interval
    label: Interval
    type: interval
    options: "1m,5m,15m,1h"
    default: "5m"
```

### Variable Chaining

Variables can depend on each other for drill-down workflows:

```
$cluster → $namespace → $service → $pod → $container
```

Each variable's query filters by the selections above it, narrowing the scope progressively.

---

## Refresh Intervals and Time Ranges

### Recommended Settings

| Dashboard Type | Refresh Interval | Default Time Range | Max Time Range |
|---------------|------------------|--------------------|----------------|
| Executive overview | 5m | 7d | 90d |
| Service overview | 30s | 1h | 7d |
| Component detail | 10s | 15m | 24h |
| Incident / debug | 5s | 5m | 1h |
| Capacity planning | Off (manual) | 30d | 1y |

### Performance Considerations

- **High cardinality queries** degrade with wide time ranges. Cap at 6h for high-cardinality dashboards
- **Recording rules** pre-aggregate expensive queries so dashboards load fast
- **Step interval** should match refresh rate (do not query at 1s resolution for a 30s refresh)
- **Caching** enable query caching for dashboards accessed by many users

```promql
# Recording rule: pre-aggregate error rate per service
# prometheus-rules.yaml
groups:
  - name: recording-rules
    rules:
      - record: service:http_error_rate:5m
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
          /
          sum(rate(http_requests_total[5m])) by (service)
```

---

## Annotation Overlays

Annotations mark events (deploys, incidents, config changes) on dashboard graphs to correlate with metric changes.

### Deploy Annotations

```bash
# Post deploy annotation to Grafana
curl -X POST http://grafana:3000/api/annotations \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "dashboardUID": "order-service-overview",
    "time": '"$(date +%s000)"',
    "tags": ["deploy", "order-service"],
    "text": "Deployed order-service v2.4.1 (commit: abc1234)"
  }'
```

### CI/CD Integration

```yaml
# .github/workflows/deploy.yaml (add after successful deploy step)
- name: Create Grafana deploy annotation
  run: |
    curl -s -X POST "$GRAFANA_URL/api/annotations" \
      -H "Authorization: Bearer ${{ secrets.GRAFANA_API_KEY }}" \
      -H "Content-Type: application/json" \
      -d '{
        "tags": ["deploy", "${{ env.SERVICE_NAME }}"],
        "text": "Deploy ${{ env.SERVICE_NAME }} ${{ github.sha }}"
      }'
```

### Annotation Types to Track

| Event Type | Tag | Color | Source |
|-----------|-----|-------|--------|
| Deployment | `deploy` | Blue | CI/CD pipeline |
| Incident started | `incident-start` | Red | PagerDuty webhook |
| Incident resolved | `incident-resolved` | Green | PagerDuty webhook |
| Config change | `config` | Orange | Config management |
| Feature flag toggle | `feature-flag` | Purple | LaunchDarkly webhook |
| Scaling event | `scale` | Yellow | Kubernetes HPA |

---

## Related Resources

- [SLO Design Guide](./slo-design-guide.md) - Defining SLOs for dashboard targets
- [Alerting Strategies](./alerting-strategies.md) - Alert design and routing
- [Core Observability Patterns](./core-observability-patterns.md) - Metrics, logs, traces fundamentals
- [Log Aggregation Patterns](./log-aggregation-patterns.md) - Logging pipelines for dashboard correlation
- [Performance Profiling Guide](./performance-profiling-guide.md) - Deep debugging beyond dashboards
- [SKILL.md](../SKILL.md) - Parent skill overview
