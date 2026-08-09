# Semantic Layer Migration Checklist

## Before Build

- [ ] Inventory current dashboard SQL and duplicated KPI logic
- [ ] Pick the target semantic platform
- [ ] Lock canonical metric names, owners, and definitions
- [ ] Decide which consumers stay on marts only

## Build

- [ ] Define entities, measures, dimensions, and default time fields
- [ ] Add descriptions, owners, and access boundaries
- [ ] Add quality checks on upstream marts
- [ ] Configure preview / validation environment

## Validation

- [ ] Compare old and new outputs over agreed date range
- [ ] Validate top dashboards and AI / NLQ prompts
- [ ] Check latency and cache behavior
- [ ] Publish migration notes to consumers

## Cutover

- [ ] Enable new semantic assets in production
- [ ] Freeze ad-hoc duplicate definitions
- [ ] Monitor query failures, metric deltas, and consumer confusion
- [ ] Set a retirement date for legacy definitions
