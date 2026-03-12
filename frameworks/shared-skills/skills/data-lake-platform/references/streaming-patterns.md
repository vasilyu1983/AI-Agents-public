# Streaming Patterns

## Tool Comparison

| Feature | Apache Kafka | Apache Flink | Spark Streaming |
|---------|-------------|--------------|-----------------|
| **Type** | Message broker | Stream processor | Micro-batch |
| **Latency** | ms | ms | seconds |
| **State** | Log-based | Built-in | Checkpoint |
| **SQL** | ksqlDB | Flink SQL | Spark SQL |
| **Best for** | Event transport | Complex CEP | Batch + stream |

---

## Apache Kafka

### Producer Pattern

```python
from confluent_kafka import Producer

config = {
    'bootstrap.servers': 'kafka:9092',
    'client.id': 'my-producer',
    'acks': 'all',
    'retries': 3
}

producer = Producer(config)

def delivery_callback(err, msg):
    if err:
        print(f'Delivery failed: {err}')

# Send messages
for event in events:
    producer.produce(
        topic='events',
        key=str(event['user_id']).encode(),
        value=json.dumps(event).encode(),
        callback=delivery_callback
    )
producer.flush()
```

### Consumer Pattern

```python
from confluent_kafka import Consumer

config = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'my-consumer-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
}

consumer = Consumer(config)
consumer.subscribe(['events'])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            print(f'Error: {msg.error()}')
            continue

        event = json.loads(msg.value())
        process_event(event)
        consumer.commit()
finally:
    consumer.close()
```

### Kafka Connect (Source)

```json
{
  "name": "postgres-source",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "${file:/secrets/db.properties:password}",
    "database.dbname": "production",
    "table.include.list": "public.orders",
    "topic.prefix": "cdc",
    "plugin.name": "pgoutput"
  }
}
```

### Kafka Connect (Sink to ClickHouse)

```json
{
  "name": "clickhouse-sink",
  "config": {
    "connector.class": "com.clickhouse.kafka.connect.ClickHouseSinkConnector",
    "tasks.max": "2",
    "topics": "events",
    "hostname": "clickhouse",
    "port": "8123",
    "database": "default",
    "table": "events",
    "username": "default",
    "password": "${file:/secrets/ch.properties:password}"
  }
}
```

---

## Apache Flink

### Stream Processing (Python)

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

env = StreamExecutionEnvironment.get_execution_environment()
t_env = StreamTableEnvironment.create(env)

# Define Kafka source
t_env.execute_sql("""
CREATE TABLE events (
    event_id STRING,
    user_id BIGINT,
    event_type STRING,
    created_at TIMESTAMP(3),
    WATERMARK FOR created_at AS created_at - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'events',
    'properties.bootstrap.servers' = 'kafka:9092',
    'properties.group.id' = 'flink-consumer',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json'
)
""")

# Define ClickHouse sink
t_env.execute_sql("""
CREATE TABLE event_counts (
    window_start TIMESTAMP(3),
    event_type STRING,
    event_count BIGINT
) WITH (
    'connector' = 'jdbc',
    'url' = 'jdbc:clickhouse://clickhouse:8123/default',
    'table-name' = 'event_counts',
    'username' = 'default',
    'password' = ''
)
""")

# Windowed aggregation
t_env.execute_sql("""
INSERT INTO event_counts
SELECT
    TUMBLE_START(created_at, INTERVAL '1' MINUTE) AS window_start,
    event_type,
    COUNT(*) AS event_count
FROM events
GROUP BY
    TUMBLE(created_at, INTERVAL '1' MINUTE),
    event_type
""")
```

### Flink SQL (Stateful Processing)

```sql
-- Sessionization
SELECT
    user_id,
    SESSION_START(created_at, INTERVAL '30' MINUTE) AS session_start,
    SESSION_END(created_at, INTERVAL '30' MINUTE) AS session_end,
    COUNT(*) AS events_in_session
FROM events
GROUP BY
    user_id,
    SESSION(created_at, INTERVAL '30' MINUTE);

-- Pattern matching (CEP)
SELECT *
FROM events
MATCH_RECOGNIZE (
    PARTITION BY user_id
    ORDER BY created_at
    MEASURES
        A.event_type AS first_event,
        B.event_type AS second_event
    ONE ROW PER MATCH
    PATTERN (A B)
    DEFINE
        A AS event_type = 'page_view',
        B AS event_type = 'purchase'
);
```

---

## Spark Structured Streaming

### Basic Stream

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .appName("StreamingApp") \
    .getOrCreate()

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "events") \
    .option("startingOffsets", "earliest") \
    .load()

# Parse JSON
events = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Windowed aggregation
result = events \
    .withWatermark("created_at", "10 minutes") \
    .groupBy(
        window("created_at", "1 minute"),
        "event_type"
    ).count()

# Write to Iceberg
result.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .option("checkpointLocation", "s3://bucket/checkpoints/") \
    .toTable("catalog.db.event_counts")
```

### Streaming to ClickHouse

```python
def write_to_clickhouse(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:clickhouse://clickhouse:8123/default") \
        .option("dbtable", "events") \
        .option("driver", "com.clickhouse.jdbc.ClickHouseDriver") \
        .mode("append") \
        .save()

events.writeStream \
    .foreachBatch(write_to_clickhouse) \
    .option("checkpointLocation", "s3://bucket/checkpoints/") \
    .start()
```

---

## Architecture Patterns

### Kappa with Iceberg

```text
Kafka → Flink → Iceberg → ClickHouse/Trino
         │
         └── Real-time serving (optional)

Benefits:
- Single processing path
- Reprocessing via Kafka replay
- ACID on Iceberg
```

### Lambda with ClickHouse

```text
                    ┌─→ Flink → ClickHouse (speed)
                    │
Kafka ──────────────┤
                    │
                    └─→ Spark → Iceberg → ClickHouse (batch)

Benefits:
- Real-time + accurate historical
- ClickHouse handles both layers
```

---

## Best Practices

1. **Use watermarks** for late data handling
2. **Set checkpoints** for fault tolerance
3. **Monitor consumer lag** (Kafka offset lag)
4. **Size partitions** appropriately (aim for 1MB messages)
5. **Use idempotent writes** (exactly-once semantics)
6. **Compact Kafka topics** for CDC
