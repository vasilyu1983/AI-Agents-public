# Data Governance & Catalog

## Tool Comparison

| Feature | DataHub | OpenMetadata | Unity Catalog |
|---------|---------|--------------|---------------|
| Type | Metadata platform | Data catalog | Catalog/governance (vendor-centered) |
| Lineage | Yes | Yes | Yes (within supported engines) |
| Search | Yes | Yes | Yes |
| Access control | Policy workflows | Policy workflows | Native (within platform) |
| Open source | Yes | Yes | Varies by distribution; validate licensing and deployment model |
| Self-hosted | Yes | Yes | Varies by distribution; validate operational requirements |

---

## DataHub

### Ingestion Configuration

```yaml
# datahub/recipes/clickhouse.yaml
source:
  type: clickhouse
  config:
    host_port: clickhouse:9000
    database: analytics
    username: datahub
    password: ${CLICKHOUSE_PASSWORD}
    include_tables: true
    include_views: true
    profiling:
      enabled: true

sink:
  type: datahub-rest
  config:
    server: http://datahub-gms:8080
```

### Python SDK

```python
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import DatasetPropertiesClass

emitter = DatahubRestEmitter("http://datahub-gms:8080")

# Emit dataset metadata
emitter.emit_mcp(
    MetadataChangeProposalWrapper(
        entityUrn="urn:li:dataset:(urn:li:dataPlatform:clickhouse,analytics.events,PROD)",
        aspect=DatasetPropertiesClass(
            description="Event stream data",
            customProperties={"owner": "data-team"}
        )
    )
)
```

---

## OpenMetadata

### Ingestion

```yaml
# openmetadata/clickhouse-ingestion.yaml
source:
  type: clickhouse
  serviceName: clickhouse-analytics
  serviceConnection:
    config:
      type: Clickhouse
      hostPort: clickhouse:9000
      username: openmetadata
      password: ${CLICKHOUSE_PASSWORD}
      databaseSchema: analytics

processor:
  type: orm-profiler
  config:
    profiler:
      includeViews: true

sink:
  type: metadata-rest
  config: {}

workflowConfig:
  openMetadataServerConfig:
    hostPort: http://openmetadata:8585/api
    authProvider: openmetadata
    securityConfig:
      jwtToken: ${JWT_TOKEN}
```

---

## Data Quality

### Great Expectations

```python
import great_expectations as gx

context = gx.get_context()

# Create expectation suite
suite = context.add_expectation_suite("events_quality")

# Add expectations
validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="events_quality"
)

validator.expect_column_values_to_not_be_null("event_id")
validator.expect_column_values_to_be_unique("event_id")
validator.expect_column_values_to_be_in_set(
    "status", ["pending", "completed", "failed"]
)
validator.expect_column_values_to_be_between(
    "amount", min_value=0, max_value=1000000
)

validator.save_expectation_suite()
```

### Soda

```yaml
# soda/checks.yaml
checks for events:
  - row_count > 0
  - missing_count(event_id) = 0
  - duplicate_count(event_id) = 0
  - invalid_count(status) = 0:
      valid values: [pending, completed, failed]
  - freshness(created_at) < 1h
```

---

## Best Practices

1. **Catalog everything** - Tables, columns, pipelines
2. **Track lineage** - Source to consumption
3. **Define ownership** - Clear data stewards
4. **Enforce policies** - Access control, PII tagging
5. **Monitor freshness** - SLA tracking
6. **Document schemas** - Descriptions, business terms
