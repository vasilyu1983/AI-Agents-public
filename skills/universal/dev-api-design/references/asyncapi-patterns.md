# AsyncAPI & Event-Driven Contract Patterns

> Operational reference for event-driven API contracts. Use when your system communicates through brokers, streams, webhooks, or asynchronous workflows instead of pure request/response HTTP.

**Version check:** examples use AsyncAPI 3.x syntax; check [asyncapi/spec releases](https://github.com/asyncapi/spec/releases) for the current version before pinning one.

## When to Use AsyncAPI

- Kafka, NATS, RabbitMQ, AMQP, MQTT, or WebSocket message contracts
- Systems where producers and consumers evolve independently
- Integrations that depend on event schemas, delivery guarantees, and correlation IDs
- Platforms with both a control-plane API and an event-plane contract

Use OpenAPI for synchronous HTTP endpoints. Use AsyncAPI for the event plane. Many production systems need both.

## Contract Structure

- Channels define where messages move
- Messages define payload shape and headers
- Operations define what the application does: `action: send` (it publishes to the channel) or `action: receive` (it consumes from the channel). AsyncAPI 3.0 replaced the 2.x `publish` / `subscribe` keywords, whose meaning was inverted from the application's point of view
- Bindings define broker-specific details without leaking them into every message schema

```yaml
channels:
  orders.created:
    address: orders.created
    messages:
      orderCreated:
        $ref: '#/components/messages/OrderCreated'
operations:
  sendOrderCreated:
    action: send
    channel:
      $ref: '#/channels/orders.created'
```

## Event Design Rules

- Use past-tense names for facts (`order.created`, `invoice.paid`)
- Use imperative names only for commands (`order.create.requested`) when command messaging is intentional
- Include globally unique event IDs
- Include correlation IDs and causation IDs when workflows span services
- Include schema or API version metadata when multiple consumers exist

## Delivery and Evolution

- Design for at-least-once delivery unless the broker guarantees more
- Make consumers idempotent
- Document ordering guarantees explicitly
- Prefer additive payload changes; do not silently repurpose existing fields
- Reserve time for consumer migration before removing fields or event types

## Operability Checklist

- Retry policy documented
- DLQ / poison-message handling documented
- Consumer timeout and backoff guidance documented
- Replay behavior documented
- PII handling and retention policy documented
- Trace propagation documented across events and webhooks

## Control Plane + Event Plane

A common production pattern is:

- REST/OpenAPI for writes, queries, admin operations, and onboarding
- AsyncAPI for downstream events and subscriptions
- Webhooks for third-party push when you cannot assume a broker

## Cross-References

- `dev-api-design/references/webhook-patterns.md` — delivery, signing, retries, DLQs
- `dev-api-design/references/real-time-api-patterns.md` — SSE, WebSocket, and streaming decisions
- `dev-api-design/references/openapi-guide.md` — synchronous HTTP contracts
