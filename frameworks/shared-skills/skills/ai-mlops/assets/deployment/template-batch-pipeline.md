# Batch Scoring Pipeline Template

Template for a production batch ML scoring job in an orchestrator (Airflow/Dagster/Prefect).

---

## 1. Pipeline Overview

**Pipeline Name:** <name>  
**Schedule:** <cron expression>  
**Output Table:** <destination>  

---

## 2. DAG Structure

extract_raw_data
→ build_features
→ run_scoring
→ write_predictions
→ validate_output

---

## 3. Step Definitions

### extract_raw_data

- Query source dataset  
- Validate freshness & volume  
- Drop duplicates  

### build_features

- Apply feature pipeline  
- Fetch lookup tables  
- Version feature transformations  

### run_scoring

- Load model version <vX.Y>  
- Generate predictions  
- Log execution metadata  

### write_predictions

- Write to feature store / warehouse  
- Partition by ds=<date>  

### validate_output

Checks:

- Row counts  
- Null values  
- Distribution drift vs previous run  

---

## 4. Idempotency Requirements

- Running job twice should produce identical output  
- Use deterministic feature pipeline  
- Store run metadata  

---

## 5. Failure Handling

- Retry with exponential backoff  
- Write to DLQ (dead-letter queue)  
- Send alert to on-call  

---

## 6. Backfill Instructions

1. Select date range  
2. Run pipeline with override flags  
3. Validate backfill consistency  
4. Document anomalies  

---

## 7. SLA

- Max runtime: <X minutes>  
- Data freshness: <threshold>  
