# RED, USE, and Golden Signals

Frameworks for deciding which metrics to instrument and alert on. Each was designed for a different class of system component; using the wrong framework for a component produces either noise or blind spots.

## When to Use Each

**RED** (Rate, Errors, Duration) targets request-driven services — anything that receives inbound calls and returns responses: HTTP APIs, gRPC services, message consumers measured per-message. Start here for user-facing services because the three signals map directly onto the end-user experience: is the service getting called, are calls succeeding, and are they fast enough. RED metrics feed SLI/SLO calculations directly.

**USE** (Utilization, Saturation, Errors) targets resources — CPUs, memory, disks, network interfaces, thread pools, database connection pools, and similar fixed-capacity components. Start here when diagnosing infrastructure bottlenecks or capacity limits rather than service behavior. Saturation in particular often reveals the root cause that RED symptoms point toward.

**Golden Signals** (Latency, Traffic, Errors, Saturation) is the Google SRE synthesis. It covers the same ground as RED + saturation but with latency split from traffic and errors, making it the most complete single-framework view for a service that is also resource-sensitive. Use Golden Signals as the dashboard template for any service that must be monitored holistically or when you cannot afford separate RED and USE dashboards.

In practice: instrument and alert on RED for your services, instrument USE for your infrastructure and shared resources, and use Golden Signals as the top-level summary layer that ties both together.

## Comparison Table

| Dimension | RED | USE | Golden Signals |
|-----------|-----|-----|----------------|
| Primary target | Request-driven services (APIs, consumers) | Resources (CPU, memory, pool, disk) | Any service end-to-end |
| Signals | Rate, Errors, Duration | Utilization, Saturation, Errors | Latency, Traffic, Errors, Saturation |
| SLO alignment | Direct — Duration → latency SLI, Errors → error-rate SLI | Indirect — saturation/utilization inform capacity SLOs | Direct — covers all four SLI types |
| Best for | User-facing request health | Infrastructure and capacity analysis | Unified service dashboards |
| Blind spots | Misses resource exhaustion as root cause | Misses request-level latency and error semantics | Requires more metrics to implement fully |
| Origin | Tom Wilkie (Grafana) | Brendan Gregg | Google SRE Book ch. 6 |
| Key references | [grafana.com/blog/2018/08/02/the-red-method](https://grafana.com/blog/2018/08/02/the-red-method-key-metrics-for-microservices-architecture/) | [brendangregg.com/usemethod.html](https://www.brendangregg.com/usemethod.html) | [sre.google/sre-book/monitoring-distributed-systems/](https://sre.google/sre-book/monitoring-distributed-systems/) |

## Practical Mapping to OpenTelemetry Metrics

| Signal | Metric type | OTel semantic-convention metric |
|--------|-------------|--------------------------|
| Rate (RED) / Traffic (Golden) | Histogram count | Count of `http.server.request.duration`; there is no separate request-count metric. In Prometheus this is `http_server_request_duration_seconds_count` |
| Errors (RED/USE/Golden) | Histogram count, filtered | Same count, filtered on `http.response.status_code >= 500` or on `error.type` being set |
| Duration / Latency | Histogram | `http.server.request.duration` |
| Utilization (USE) | Gauge | `system.cpu.utilization`, `jvm.memory.used` |
| Saturation (USE/Golden) | Gauge / UpDownCounter | `http.server.active_requests`, `db.client.connection.count` (with `db.client.connection.state`), `db.client.connection.pending_requests`, `jvm.thread.count` |

Use semantic conventions for all metric names; avoid inventing parallel names for standard protocol signals. Names change between semconv releases, so check the [HTTP](https://opentelemetry.io/docs/specs/semconv/http/http-metrics/), [database](https://opentelemetry.io/docs/specs/semconv/database/database-metrics/) and [JVM](https://opentelemetry.io/docs/specs/semconv/runtime/jvm-metrics/) metric pages before building dashboards on them.
