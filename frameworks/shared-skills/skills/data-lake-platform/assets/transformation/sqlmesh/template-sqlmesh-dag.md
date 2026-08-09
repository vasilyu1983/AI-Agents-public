# SQLMesh DAG & Dependencies Template

*Purpose: Manage model dependencies and execution order in SQL transformations.*

## Model Dependencies

### Automatic from refs()
```sql
MODEL (
  name marts.customer_ltv
);

SELECT
  c.customer_id,
  c.email,
  SUM(o.order_total) AS lifetime_value
FROM {{ ref('staging', 'stg_customers') }} c
LEFT JOIN {{ ref('staging', 'stg_orders') }} o
  ON c.customer_id = o.customer_id
GROUP BY 1, 2;
```

## Visualize DAG

```bash
# Start UI to see lineage
sqlmesh ui

# Generate static DAG
sqlmesh dag
```

## Execution Order

SQLMesh automatically determines execution order:
1. staging models (no dependencies)
2. intermediate models (depend on staging)
3. marts models (depend on intermediate)

## Best Practices

- BEST: Use ref() for all model references
- BEST: Organize by layer (staging → intermediate → marts)
- BEST: Avoid circular dependencies
- BEST: Use views for frequently referenced joins
- BEST: Document dependencies in model descriptions
