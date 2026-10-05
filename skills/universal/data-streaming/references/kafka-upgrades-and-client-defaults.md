# Kafka Upgrades, Protocol Adoption, And Client Defaults

Decision rules for Kafka broker upgrades, the ZooKeeper-to-KRaft migration, consumer-protocol and share-group adoption, and producer defaults that differ by client. Release status changes often, so check the Apache Kafka release announcements (https://kafka.apache.org/blog/releases/) and the upgrade notes for the exact target version before naming a version or calling a feature GA.

## Table of Contents

1. [ZooKeeper to KRaft Migration](#zookeeper-to-kraft-migration)
2. [Upgrade Traps](#upgrade-traps)
3. [Consumer Rebalance Protocol (KIP-848)](#consumer-rebalance-protocol-kip-848)
4. [Share Group Adoption (KIP-932)](#share-group-adoption-kip-932)
5. [Tiered Storage and Replay Consumers](#tiered-storage-and-replay-consumers)
6. [Producer Defaults Are Client Settings](#producer-defaults-are-client-settings)

---

## ZooKeeper to KRaft Migration

- Kafka 4.x runs only in KRaft mode, and the migration needs a bridge release; 3.9 is the last one. A ZooKeeper cluster cannot upgrade straight to 4.x: finalize the migration on a bridge release (3.9 unless the upgrade notes allow an earlier one), then do a normal rolling upgrade.
- Follow the official 3.9 procedure (https://kafka.apache.org/39/operations/kraft/), not a summary. Its shape: brokers on the 3.9 line with `inter.broker.protocol.version=3.9`; a KRaft controller quorum formatted with the existing cluster ID; `zookeeper.metadata.migration.enable=true` on controllers and brokers; then hybrid, dual-write (rollback still possible), and finalized phases.
- There is no `kafka-storage.sh --migrate-from-zookeeper` flag and no "read-only bridge mode". Treat a runbook that mentions them as wrong.
- Mixed ZooKeeper-mode and 4.x KRaft brokers are not supported.
- KIP-919 adds `bootstrap.controllers` so an admin client can talk to the controller quorum directly. Setting it together with `bootstrap.servers` is an error; broker-bootstrapped admin clients need no change.

Application teams do not own the migration, but they must know:

- KRaft does not change the client wire protocol. Services need no code change; confirm the client library version against the vendor's client/broker compatibility matrix.
- `bootstrap.servers` does not change, and committed offsets live in `__consumer_offsets`, so no offset reset is needed.
- ZooKeeper connection strings and ZooKeeper-era admin helpers in test setup fail against KRaft; use `bootstrap.servers`.
- Transactional producers (`transactional.id`) should be watched through the controller cutover; coordinate with the platform team.

## Upgrade Traps

- **"Kafka 4.x" is not one state.** Share-group readiness, consumer-protocol behavior, and Streams features differ across minors. Name the exact broker minor before promising a feature.
- **`metadata.version` finalization.** After every node runs the new version, advance the feature level with `kafka-features.sh`. Do not leave the cluster in a mixed-version state beyond the upgrade window.
- **Custom authorizers** (`authorizer.class.name`) written against ZooKeeper-era classes must be checked against the KRaft authorizer before the upgrade.
- **Group coordinator internals changed** under KRaft. Rebalance and commit semantics are equivalent, but run load and rebalance tests after the upgrade.
- **Managed-service lag.** Managed Kafka offerings support a narrower version set than the OSS release train and often lag it. Check the provider's supported-version page, not only the OSS changelog.

## Consumer Rebalance Protocol (KIP-848)

- The consumer protocol is opt-in: `group.protocol=consumer` in the Java client, `GroupProtocol=Consumer` in librdkafka-based clients such as Confluent .NET. The classic protocol stays the client default until the release notes say otherwise.
- It needs broker support. Client-side assignor and session settings move to the broker, so review consumer configs before switching.
- KIP-1274 plans the default flip and later removal of the classic protocol. Check its current status before quoting a release or deadline, and note that warnings logged by the Java client are not emitted by librdkafka-based clients.

## Share Group Adoption (KIP-932)

Broker readiness and client support are separate milestones. Before recommending share groups:

1. Confirm the broker minor marks share groups production-ready (release notes, not a blog post).
2. Confirm the exact client library version exposes a share-consumer API. The Java client has `ShareConsumer`; a preview C API in librdkafka is not a language binding, so check the Confluent .NET/Python/Go changelog for the version in use.
3. Confirm every consumer of the topic tolerates out-of-order processing. If any consumer needs per-entity ordering, use a classic consumer group.
4. Map failure handling to per-record acknowledgement: accept, release, or reject, with a delivery-count limit. Retry-topic and DLQ designs built on offset commits do not carry over unchanged.

Decision rule: ordered work stays on classic groups. Order-insensitive work queues are share-group candidates only when steps 1 and 2 both pass. Until then, a classic group with a bounded worker pool inside the handler is the closest approximation, with parallelism still bound by partition count. For sizing, share groups are the one Kafka mode where pooled (M/M/c) models apply; see `queueing-theory-applied.md`.

## Tiered Storage and Replay Consumers

- Tiered storage (KIP-405) became production-ready in 3.9, not 4.0. It is a broker feature; the producer and consumer APIs do not change.
- Consumers that read old offsets (replay, audit, backfill) may see higher fetch latency when segments come from the remote tier. Budget fetch, request, and handler timeouts for it, and check `remote.storage.enable` on the topic before tuning.
- Replay rebalances come from `max.poll.interval.ms`, not `session.timeout.ms`: heartbeats run on a background thread, so slow remote fetches alone do not expire the session. A handler or consume loop that stalls past the poll interval does.

## Producer Defaults Are Client Settings

- Idempotence and `acks` are client settings. A broker upgrade does not change them.
- The Java producer declared `enable.idempotence=true` and `acks=all` as defaults in 3.0; a bug (KAFKA-13598) left idempotence off unless set explicitly until 3.0.1, 3.1.1, and 3.2.0. librdkafka-based clients (Confluent .NET, Python, Go) default to `enable.idempotence=false`; check `CONFIGURATION.md` for the client version in use.
- Kafka 4.0 did not make producers idempotent. Its Java producer changes: `linger.ms` default 0 → 5, and idempotence with `max.in.flight.requests.per.connection > 5` is now rejected instead of silently disabled.
- Idempotence deduplicates the client's internal retries within one producer session. An application-level re-send (a new `send`/`ProduceAsync` call after a failure) is a new record and duplicates even with idempotence on. Prefer the client's internal retries within `delivery.timeout.ms`.
- Declare idempotence and `acks` explicitly on critical producers so intent survives client upgrades, and pair `acks=all` with a `min.insync.replicas` that leaves write headroom (see P1 in `distributed-systems-applied.md`).
