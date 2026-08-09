# Kafka Ingestion Template

## Overview

Apache Kafka patterns for real-time data ingestion into data lakes.

## Producer Patterns

### Python Producer

```python
from confluent_kafka import Producer
import json

config = {
    'bootstrap.servers': 'kafka:9092',
    'client.id': 'events-producer',
    'acks': 'all',
    'retries': 3,
    'retry.backoff.ms': 1000,
    'enable.idempotence': True,
    'compression.type': 'zstd'
}

producer = Producer(config)

def delivery_callback(err, msg):
    if err:
        print(f'Delivery failed: {err}')
    else:
        print(f'Delivered to {msg.topic()}[{msg.partition()}]')

def produce_event(event):
    producer.produce(
        topic='events',
        key=str(event['user_id']).encode(),
        value=json.dumps(event).encode(),
        callback=delivery_callback
    )

# Batch produce
for event in events:
    produce_event(event)
    producer.poll(0)  # Trigger callbacks

producer.flush()  # Wait for all deliveries
```

### Avro Producer

```python
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

schema_registry_conf = {'url': 'http://schema-registry:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

avro_schema = """
{
    "type": "record",
    "name": "Event",
    "fields": [
        {"name": "event_id", "type": "string"},
        {"name": "user_id", "type": "long"},
        {"name": "event_type", "type": "string"},
        {"name": "created_at", "type": "long", "logicalType": "timestamp-millis"}
    ]
}
"""

avro_serializer = AvroSerializer(
    schema_registry_client,
    avro_schema
)

producer = Producer({'bootstrap.servers': 'kafka:9092'})

def produce_avro_event(event):
    producer.produce(
        topic='events',
        key=str(event['user_id']).encode(),
        value=avro_serializer(event, None)
    )
```

---

## Consumer Patterns

### Python Consumer

```python
from confluent_kafka import Consumer, KafkaError

config = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'data-lake-consumer',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'max.poll.interval.ms': 300000
}

consumer = Consumer(config)
consumer.subscribe(['events'])

try:
    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            print(f'Error: {msg.error()}')
            continue

        event = json.loads(msg.value())
        process_event(event)

        # Manual commit after processing
        consumer.commit(asynchronous=False)

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
```

### Batch Consumer

```python
from confluent_kafka import Consumer
import time

consumer = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'batch-consumer',
    'enable.auto.commit': False,
    'fetch.min.bytes': 1048576,  # 1 MB
    'fetch.wait.max.ms': 500
})

consumer.subscribe(['events'])

batch = []
batch_size = 1000
last_commit = time.time()
commit_interval = 10  # seconds

while True:
    msg = consumer.poll(timeout=0.1)

    if msg is not None and not msg.error():
        batch.append(json.loads(msg.value()))

    # Flush batch on size or time
    should_flush = (
        len(batch) >= batch_size or
        (time.time() - last_commit) >= commit_interval
    )

    if should_flush and batch:
        # Write batch to data lake
        write_to_lake(batch)
        consumer.commit()
        batch = []
        last_commit = time.time()
```

---

## Kafka Connect

### Source Connector (Debezium CDC)

```json
{
  "name": "postgres-cdc-source",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "${file:/secrets/db.properties:password}",
    "database.dbname": "production",
    "database.server.name": "prod",
    "table.include.list": "public.users,public.orders",
    "plugin.name": "pgoutput",
    "publication.name": "dbz_publication",
    "slot.name": "dbz_slot",
    "topic.prefix": "cdc",
    "transforms": "unwrap",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones": "true"
  }
}
```

### Sink Connector (S3)

```json
{
  "name": "s3-sink",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "4",
    "topics": "events",
    "s3.bucket.name": "data-lake-bronze",
    "s3.region": "us-east-1",
    "s3.part.size": "5242880",
    "flush.size": "10000",
    "rotate.interval.ms": "60000",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "parquet.codec": "zstd",
    "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
    "path.format": "'year'=YYYY/'month'=MM/'day'=dd/'hour'=HH",
    "partition.duration.ms": "3600000",
    "locale": "en-US",
    "timezone": "UTC"
  }
}
```

### Sink Connector (ClickHouse)

```json
{
  "name": "clickhouse-sink",
  "config": {
    "connector.class": "com.clickhouse.kafka.connect.ClickHouseSinkConnector",
    "tasks.max": "4",
    "topics": "events",
    "hostname": "clickhouse",
    "port": "8123",
    "database": "bronze",
    "username": "default",
    "password": "${file:/secrets/ch.properties:password}",
    "ssl": "false",
    "tableMapping": "events=raw_events"
  }
}
```

---

## Topic Configuration

### Create Topic

```bash
kafka-topics.sh --create \
  --bootstrap-server kafka:9092 \
  --topic events \
  --partitions 16 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config cleanup.policy=delete \
  --config compression.type=zstd \
  --config min.insync.replicas=2
```

### Compacted Topic (CDC)

```bash
kafka-topics.sh --create \
  --bootstrap-server kafka:9092 \
  --topic cdc.users \
  --partitions 8 \
  --replication-factor 3 \
  --config cleanup.policy=compact \
  --config min.compaction.lag.ms=3600000 \
  --config delete.retention.ms=86400000
```

---

## Monitoring

### Consumer Lag

```bash
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group data-lake-consumer
```

### Prometheus Metrics

```yaml
# prometheus/kafka-alerts.yaml
groups:
  - name: kafka
    rules:
      - alert: KafkaConsumerLag
        expr: kafka_consumergroup_lag > 100000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High consumer lag on {{ $labels.topic }}"

      - alert: KafkaUnderReplicatedPartitions
        expr: kafka_server_replicamanager_underreplicatedpartitions > 0
        for: 5m
        labels:
          severity: critical
```

---

## Best Practices

1. **Use Avro/Protobuf** - Schema enforcement and evolution
2. **Enable idempotence** - Exactly-once semantics
3. **Set appropriate partitions** - 1 partition per 10 MB/s throughput
4. **Monitor consumer lag** - Alert on high lag
5. **Use compaction for CDC** - Keep latest state per key
6. **Configure retention** - Based on replay requirements
