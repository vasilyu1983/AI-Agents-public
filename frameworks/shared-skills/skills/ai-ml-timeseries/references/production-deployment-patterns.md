# Production Time Series Deployment Patterns

Operational patterns for deploying, monitoring, and maintaining time series forecasting systems in production.

---

## Overview

Production time series systems require:
- Automated feature pipelines
- Scheduled retraining
- Drift monitoring
- Fallback strategies
- Data quality checks
- Streaming ingestion handling

---

## Pattern 1: Feature Pipeline Architecture

### Key Principles
- Same code for training and serving
- Idempotent operations
- Historical replay capability
- Version control for features

### Implementation

```python
# feature_pipeline.py
from datetime import datetime, timedelta
import pandas as pd

class TimeSeriesFeaturePipeline:
    def __init__(self, config):
        self.config = config
        self.feature_version = config['feature_version']

    def create_features(self, df, end_date=None):
        """
        Create features for both training and serving
        Same code path for consistency
        """
        if end_date is None:
            end_date = datetime.now()

        # Feature engineering (identical for train/serve)
        df = self._add_lag_features(df, end_date)
        df = self._add_rolling_features(df, end_date)
        df = self._add_calendar_features(df, end_date)

        # Version stamp
        df['feature_version'] = self.feature_version

        return df

    def _add_lag_features(self, df, end_date):
        """Ensure no future leakage"""
        df = df[df.index <= end_date].copy()
        for lag in [1, 7, 28]:
            df[f'lag_{lag}'] = df['target'].shift(lag)
        return df

    def _add_rolling_features(self, df, end_date):
        """Temporal aggregations"""
        df = df[df.index <= end_date].copy()
        for window in [7, 14, 28]:
            df[f'rolling_mean_{window}'] = df['target'].rolling(window).mean()
            df[f'rolling_std_{window}'] = df['target'].rolling(window).std()
        return df

    def _add_calendar_features(self, df, end_date):
        """Calendar features"""
        df['day_of_week'] = df.index.dayofweek
        df['month'] = df.index.month
        df['is_weekend'] = df.index.dayofweek.isin([5, 6]).astype(int)
        return df
```

### Scheduling

```yaml
# airflow_dag.py or cron schedule
# Daily feature pipeline
schedule: "0 1 * * *"  # 1 AM daily

tasks:
  - name: extract_raw_data
    source: database
    table: time_series_raw

  - name: transform_features
    code: feature_pipeline.create_features()
    output: feature_store

  - name: validate_features
    checks:
      - no_nulls_in_lag_features
      - feature_version_matches
      - date_range_complete
```

---

## Pattern 2: Model Retraining Strategy

### Time-Based Retraining

```python
class ModelRetrainingScheduler:
    def __init__(self, schedule='weekly'):
        self.schedule = schedule  # 'daily', 'weekly', 'monthly'

    def should_retrain(self, last_train_date):
        """Determine if retraining is needed"""
        today = datetime.now().date()

        if self.schedule == 'daily':
            return (today - last_train_date).days >= 1
        elif self.schedule == 'weekly':
            return (today - last_train_date).days >= 7
        elif self.schedule == 'monthly':
            return (today - last_train_date).days >= 30

        return False

    def retrain_model(self, data, config):
        """Execute retraining"""
        # Load historical data
        train_data = data[data['date'] <= datetime.now() - timedelta(days=7)]

        # Train model
        model = self._train(train_data, config)

        # Validate on recent data
        val_metrics = self._validate(model, data)

        if val_metrics['mae'] < config['max_acceptable_mae']:
            self._save_model(model)
            return True
        else:
            print("Retraining failed validation, keeping old model")
            return False
```

### Trigger-Based Retraining (Drift Detection)

```python
class DriftTriggeredRetraining:
    def __init__(self, drift_threshold=0.15):
        self.drift_threshold = drift_threshold

    def check_drift_and_retrain(self, model, recent_data):
        """
        Monitor forecast error drift
        Retrain if performance degrades
        """
        # Compute recent forecast errors
        recent_mae = self._compute_recent_mae(model, recent_data)
        baseline_mae = model.metadata['training_mae']

        # Check drift
        drift = (recent_mae - baseline_mae) / baseline_mae

        if drift > self.drift_threshold:
            print(f"Drift detected: {drift:.2%}. Retraining...")
            return self._retrain(recent_data)

        return False
```

---

## Pattern 3: Monitoring & Drift Detection

### Multi-Level Monitoring

```python
class ForecastMonitoring:
    def __init__(self):
        self.metrics = []

    def monitor(self, forecasts, actuals, features):
        """
        Track multiple drift signals
        """
        # 1. Forecast error drift
        error_drift = self._monitor_error_drift(forecasts, actuals)

        # 2. Feature drift (distribution shift)
        feature_drift = self._monitor_feature_drift(features)

        # 3. Volume drift (data pattern change)
        volume_drift = self._monitor_volume_drift(actuals)

        # 4. Horizon-specific drift
        horizon_drift = self._monitor_horizon_drift(forecasts, actuals)

        # Aggregate metrics
        self.metrics.append({
            'timestamp': datetime.now(),
            'error_drift': error_drift,
            'feature_drift': feature_drift,
            'volume_drift': volume_drift,
            'horizon_drift': horizon_drift
        })

        return self._should_alert(self.metrics[-1])

    def _monitor_error_drift(self, forecasts, actuals):
        """MAE drift over time"""
        recent_mae = np.abs(forecasts - actuals).mean()
        historical_mae = self._get_historical_mae()
        return (recent_mae - historical_mae) / historical_mae

    def _monitor_feature_drift(self, features):
        """Feature distribution drift (PSI or KS)"""
        from scipy.stats import ks_2samp

        drift_scores = {}
        for col in features.columns:
            historical_dist = self._get_historical_dist(col)
            recent_dist = features[col].values

            # Kolmogorov-Smirnov test
            ks_stat, p_value = ks_2samp(historical_dist, recent_dist)
            drift_scores[col] = ks_stat

        return max(drift_scores.values())

    def _monitor_volume_drift(self, actuals):
        """Detect sudden volume changes"""
        recent_mean = actuals[-30:].mean()
        historical_mean = actuals[-180:-30].mean()
        return abs(recent_mean - historical_mean) / historical_mean

    def _monitor_horizon_drift(self, forecasts, actuals):
        """Track error by forecast horizon"""
        horizon_errors = {}
        for h in range(forecasts.shape[1]):
            mae_h = np.abs(forecasts[:, h] - actuals[:, h]).mean()
            horizon_errors[h+1] = mae_h

        return horizon_errors
```

### Alert Thresholds

```python
MONITORING_THRESHOLDS = {
    'error_drift': 0.15,      # 15% MAE increase triggers alert
    'feature_drift': 0.10,    # 10% KS statistic
    'volume_drift': 0.20,     # 20% volume change
    'horizon_drift': {
        1: 0.10,  # Near-term: 10% acceptable
        7: 0.15,  # Week-ahead: 15%
        30: 0.25  # Month-ahead: 25%
    }
}
```

---

## Pattern 4: Fallback Strategies

### Graceful Degradation

```python
class ForecastingWithFallback:
    def __init__(self, primary_model, fallback_strategy='seasonal_naive'):
        self.primary_model = primary_model
        self.fallback_strategy = fallback_strategy

    def predict(self, X, historical_data):
        """
        Try primary model, fall back if fails
        """
        try:
            forecast = self.primary_model.predict(X)

            # Sanity checks
            if self._is_valid_forecast(forecast):
                return forecast, 'primary'
            else:
                return self._fallback(historical_data), 'fallback_sanity_check'

        except Exception as e:
            print(f"Primary model failed: {e}")
            return self._fallback(historical_data), 'fallback_exception'

    def _is_valid_forecast(self, forecast):
        """Sanity checks on forecast"""
        # No NaNs
        if np.isnan(forecast).any():
            return False

        # No extreme values
        if (forecast < 0).any() or (forecast > 1e6).any():
            return False

        # No flat forecasts (all same value)
        if forecast.std() < 1e-6:
            return False

        return True

    def _fallback(self, historical_data):
        """Fallback forecast strategies"""
        if self.fallback_strategy == 'last_known':
            return historical_data[-1]

        elif self.fallback_strategy == 'seasonal_naive':
            # Last year same period
            return historical_data[-365:]

        elif self.fallback_strategy == 'moving_average':
            return historical_data[-30:].mean()

        else:
            # Ultimate fallback: median
            return historical_data.median()
```

---

## Pattern 5: Streaming Ingestion & Backfill

### Real-Time Data Ingestion

```python
class StreamingTimeSeriesIngestion:
    def __init__(self, kafka_topic, feature_pipeline):
        self.kafka_topic = kafka_topic
        self.feature_pipeline = feature_pipeline
        self.buffer = []

    def consume_stream(self):
        """
        Consume real-time events
        Handle late arrivals and out-of-order data
        """
        from kafka import KafkaConsumer

        consumer = KafkaConsumer(
            self.kafka_topic,
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='latest'
        )

        for message in consumer:
            event = self._parse_event(message.value)

            # Handle late arrivals
            if self._is_late_arrival(event):
                self._backfill(event)
            else:
                self._process_event(event)

    def _is_late_arrival(self, event):
        """Check if event timestamp is in the past"""
        event_time = event['timestamp']
        processing_time = datetime.now()
        return (processing_time - event_time).total_seconds() > 3600  # 1 hour late

    def _backfill(self, event):
        """Handle late data with idempotent upsert"""
        # Upsert into feature store (overwrites if exists)
        self.feature_store.upsert(
            timestamp=event['timestamp'],
            features=self.feature_pipeline.create_features([event])
        )

    def _process_event(self, event):
        """Process on-time event"""
        self.buffer.append(event)

        # Micro-batch every 100 events
        if len(self.buffer) >= 100:
            self._flush_buffer()

    def _flush_buffer(self):
        """Write buffered events to feature store"""
        features = self.feature_pipeline.create_features(self.buffer)
        self.feature_store.write(features)
        self.buffer = []
```

### Historical Backfill

```python
class HistoricalBackfill:
    def __init__(self, feature_pipeline, start_date, end_date):
        self.feature_pipeline = feature_pipeline
        self.start_date = start_date
        self.end_date = end_date

    def run_backfill(self, chunk_size='1D'):
        """
        Backfill historical data with windowing
        """
        date_range = pd.date_range(self.start_date, self.end_date, freq=chunk_size)

        for chunk_start in date_range:
            chunk_end = chunk_start + pd.Timedelta(chunk_size)

            # Extract raw data for chunk
            raw_data = self._extract_raw_data(chunk_start, chunk_end)

            # Create features (same code as production)
            features = self.feature_pipeline.create_features(raw_data)

            # Validate features
            if self._validate_features(features):
                self._write_features(features)
            else:
                print(f"Backfill validation failed for {chunk_start}")

        print("Backfill complete")

    def _validate_features(self, features):
        """Ensure backfilled features match schema"""
        required_cols = self.feature_pipeline.get_feature_names()
        return all(col in features.columns for col in required_cols)
```

---

## Pattern 6: Data Residency & Governance

### Multi-Tenant Isolation

```python
class MultiTenantForecastingPipeline:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id

    def get_data(self):
        """Ensure tenant isolation"""
        query = f"""
        SELECT * FROM time_series_data
        WHERE tenant_id = '{self.tenant_id}'
        AND date >= CURRENT_DATE - INTERVAL '2 years'
        """
        return self._execute_query(query)

    def save_forecast(self, forecast):
        """Tag with tenant for isolation"""
        forecast['tenant_id'] = self.tenant_id
        self._write_to_db(forecast, table='forecasts')
```

### PII Handling

```python
class PIIHandling:
    def anonymize_features(self, df):
        """Remove or hash PII before model training"""
        pii_cols = ['customer_id', 'email', 'phone']

        for col in pii_cols:
            if col in df.columns:
                df[col] = df[col].apply(self._hash_pii)

        return df

    def _hash_pii(self, value):
        """One-way hash for PII"""
        import hashlib
        return hashlib.sha256(str(value).encode()).hexdigest()
```

### Audit Trail & Provenance

```python
class ForecastProvenance:
    def log_forecast(self, forecast, metadata):
        """Track full lineage of forecast"""
        provenance = {
            'forecast_id': uuid.uuid4(),
            'timestamp': datetime.now(),
            'model_version': metadata['model_version'],
            'feature_version': metadata['feature_version'],
            'data_source': metadata['data_source'],
            'data_date_range': metadata['data_date_range'],
            'retraining_trigger': metadata['retraining_trigger'],  # 'scheduled' or 'drift'
            'forecast': forecast
        }

        # Store in audit log
        self._write_to_audit_log(provenance)
```

---

## Checklist: Production-Ready Time Series System

### Feature Pipeline
- [ ] Same code for training and serving
- [ ] Idempotent operations (safe to re-run)
- [ ] Version control for feature definitions
- [ ] Historical replay capability
- [ ] Scheduled execution (daily/hourly)
- [ ] Data quality validation

### Model Deployment
- [ ] Retraining schedule defined (time-based or drift-based)
- [ ] Model versioning implemented
- [ ] Rollback capability for failed deployments
- [ ] A/B testing for new model versions
- [ ] Prediction caching for efficiency

### Monitoring
- [ ] Forecast error tracking (MAE, MAPE, WAPE)
- [ ] Feature drift detection (PSI, KS)
- [ ] Volume drift monitoring
- [ ] Horizon-specific error tracking
- [ ] Alerts configured with thresholds
- [ ] Dashboard for real-time monitoring

### Fallback & Resilience
- [ ] Fallback strategy defined (seasonal naive, last known, etc.)
- [ ] Sanity checks on forecasts
- [ ] Circuit breaker for model failures
- [ ] Fallback usage tracked and alerted

### Data Ingestion
- [ ] Streaming ingestion implemented (Kafka/Kinesis)
- [ ] Late arrival handling (backfill)
- [ ] Out-of-order data handling
- [ ] Idempotent upserts for duplicates
- [ ] Gap filling with business rules

### Governance
- [ ] Tenant isolation (multi-tenant systems)
- [ ] PII handling documented
- [ ] Data residency compliance (GDPR, CCPA)
- [ ] Audit trail for forecasts
- [ ] Provenance tracking (data → features → forecast)

---

## References

See also:
- [Backtesting Patterns](backtesting-patterns.md) - Validation strategies
- [Model Selection Guide](model-selection-guide.md) - Choosing models for production
- [TS EDA Best Practices](ts-eda-best-practices.md) - Data quality checks
