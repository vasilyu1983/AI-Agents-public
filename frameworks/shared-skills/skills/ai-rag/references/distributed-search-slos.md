# Distributed Search Operations & SLOs

Operational patterns for running search at scale with reliability and performance guarantees.

---

## When to Use

Apply these patterns when:
- Search serves production traffic
- Multi-shard/multi-replica deployments
- SLO requirements (latency, availability)
- Need resilience to failures
- Hot/cold tier storage architectures

---

## Pattern 1: Topology & Consistency

### Shard & Replica Design

**Sharding strategy:**

```python
# Example: Hash-based sharding
def shard_assignment(doc_id, num_shards=8):
    """
    Assign document to shard based on hash
    """
    return hash(doc_id) % num_shards

# Shard configuration
shard_config = {
    'num_shards': 8,
    'replicas_per_shard': 3,
    'placement': {
        'shard_0': ['node-1', 'node-2', 'node-3'],
        'shard_1': ['node-2', 'node-3', 'node-4'],
        # ... etc
    }
}
```

**Consistency models:**

| Model | Use Case | Trade-offs |
|-------|----------|------------|
| **Eventual consistency** | Real-time ingestion | Fast writes, stale reads possible |
| **Strong consistency** | Critical data | Slower writes, always fresh reads |
| **Read-your-writes** | User edits | User sees own changes immediately |

**Checklist**
- [ ] Shard/replica placement documented
- [ ] Consistency model chosen based on use case
- [ ] Cross-datacenter replication configured (if needed)
- [ ] Quorum reads/writes configured for strong consistency

---

## Pattern 2: Resilience & Health Checks

### Health Monitoring

```python
class SearchClusterHealth:
    def check_health(self):
        """
        Monitor cluster health
        """
        health = {
            'shards': self.check_shard_health(),
            'replicas': self.check_replica_lag(),
            'query_performance': self.check_query_latency(),
            'ingestion_lag': self.check_ingestion_lag()
        }

        return health

    def check_shard_health(self):
        """
        Verify all shards are reachable
        """
        unhealthy_shards = []
        for shard_id in range(self.num_shards):
            if not self.ping_shard(shard_id):
                unhealthy_shards.append(shard_id)

        return {
            'healthy': len(unhealthy_shards) == 0,
            'unhealthy_shards': unhealthy_shards
        }

    def check_replica_lag(self):
        """
        Monitor replica lag behind primary
        """
        max_lag_threshold = 60  # seconds

        lags = {}
        for shard_id in range(self.num_shards):
            primary_version = self.get_primary_version(shard_id)
            replicas = self.get_replicas(shard_id)

            for replica in replicas:
                lag = primary_version - replica['version']
                if lag > max_lag_threshold:
                    lags[f'shard_{shard_id}_replica_{replica["id"]}'] = lag

        return {
            'within_threshold': len(lags) == 0,
            'lagging_replicas': lags
        }
```

### Automatic Reroute on Failure

```python
def execute_query_with_failover(query, primary_shard, replica_shards):
    """
    Query with automatic failover to replicas
    """
    # Try primary first
    try:
        return query_shard(primary_shard, query, timeout=100)
    except (TimeoutError, ConnectionError):
        # Failover to replicas
        for replica in replica_shards:
            try:
                return query_shard(replica, query, timeout=100)
            except Exception:
                continue

        # All replicas failed
        raise SearchUnavailableError("All replicas failed for shard")
```

**Checklist**
- [ ] Health checks run every 10-30 seconds
- [ ] Replica lag thresholds configured (< 60s)
- [ ] Automatic reroute on shard failure
- [ ] Circuit breaker for unhealthy shards

---

## Pattern 3: Backpressure & Load Shedding

### Queue Depth Monitoring

```python
class BackpressureController:
    def __init__(self, max_queue_depth=1000, latency_threshold=500):
        self.max_queue_depth = max_queue_depth
        self.latency_threshold = latency_threshold  # ms
        self.current_queue_depth = 0

    def should_accept_query(self):
        """
        Reject queries when overloaded
        """
        # Check queue depth
        if self.current_queue_depth > self.max_queue_depth:
            return False, "Queue full"

        # Check latency
        current_latency = self.get_p95_latency()
        if current_latency > self.latency_threshold:
            return False, "Latency SLO breach"

        return True, "OK"

    def execute_with_backpressure(self, query):
        """
        Execute query with backpressure control
        """
        accept, reason = self.should_accept_query()

        if not accept:
            # Shed load
            return {
                'error': 'Service overloaded',
                'reason': reason,
                'retry_after': 5  # seconds
            }

        # Accept query
        self.current_queue_depth += 1
        try:
            result = self.execute_query(query)
            return result
        finally:
            self.current_queue_depth -= 1
```

### Load Shedding Strategies

```python
def load_shedding_strategy(query, qps_limit=1000):
    """
    Prioritize queries during overload
    """
    current_qps = get_current_qps()

    if current_qps < qps_limit:
        # Under limit, accept all
        return True

    # Over limit, prioritize
    priority = classify_query_priority(query)

    if priority == 'critical':
        return True  # Always accept critical queries
    elif priority == 'high':
        return random.random() < 0.5  # Accept 50% of high-priority
    else:
        return False  # Reject low-priority

def classify_query_priority(query):
    """
    Classify query priority based on characteristics
    """
    if query.get('user_type') == 'premium':
        return 'critical'
    elif query.get('source') == 'internal_tool':
        return 'high'
    else:
        return 'normal'
```

**Checklist**
- [ ] Queue depth monitoring active
- [ ] Backpressure triggers configured (queue, latency)
- [ ] Load shedding policy defined
- [ ] Rate limiting per client/tenant

---

## Pattern 4: Caching Strategy

### Multi-Level Caching

```python
class SearchCacheManager:
    def __init__(self):
        # L1: Result cache (short TTL)
        self.result_cache = LRUCache(max_size=10000, ttl=300)  # 5 min

        # L2: Embedding cache (longer TTL)
        self.embedding_cache = LRUCache(max_size=100000, ttl=3600)  # 1 hour

        # L3: Hot query cache (very short TTL)
        self.hot_query_cache = LRUCache(max_size=1000, ttl=60)  # 1 min

    def search_with_cache(self, query, k=10):
        """
        Multi-level cache lookup
        """
        cache_key = f"{query}:{k}"

        # L3: Hot query cache
        cached_result = self.hot_query_cache.get(cache_key)
        if cached_result:
            return cached_result, 'hot_cache_hit'

        # L1: Result cache
        cached_result = self.result_cache.get(cache_key)
        if cached_result:
            return cached_result, 'result_cache_hit'

        # L2: Embedding cache (avoid re-encoding)
        query_embedding = self.embedding_cache.get(query)
        if not query_embedding:
            query_embedding = self.encoder.encode(query)
            self.embedding_cache.put(query, query_embedding)

        # Execute search
        results = self.vector_index.search(query_embedding, k=k)

        # Cache results
        self.result_cache.put(cache_key, results)

        # If query is hot (seen recently), cache in L3
        if self.is_hot_query(query):
            self.hot_query_cache.put(cache_key, results)

        return results, 'cache_miss'
```

### Cache Invalidation

```python
def invalidate_on_index_change(index_version):
    """
    Invalidate caches when index changes
    """
    global current_index_version

    if index_version != current_index_version:
        # Clear all result caches
        result_cache.clear()
        hot_query_cache.clear()

        # Embedding cache can persist (model hasn't changed)

        current_index_version = index_version
        log_event("Cache invalidated due to index change")
```

**Checklist**
- [ ] Multi-level cache configured (results, embeddings, hot queries)
- [ ] Cache hit rates monitored (target: >60% for hot queries)
- [ ] Invalidation on index change automated
- [ ] TTLs tuned based on data freshness requirements

---

## Pattern 5: Performance Runbook

### Metrics to Track

```python
search_slos = {
    'latency': {
        'p50': 100,   # ms
        'p95': 300,   # ms
        'p99': 800    # ms
    },
    'availability': 0.999,  # 99.9%
    'relevance': {
        'ndcg@10': 0.75,
        'mrr': 0.80
    },
    'throughput': {
        'qps': 1000
    }
}
```

### Incident Playbook

```python
class SearchIncidentPlaybook:
    """
    Automated responses to SLO breaches
    """
    def handle_latency_spike(self, current_p95):
        """
        Response to latency SLO breach
        """
        actions = []

        # Action 1: Reduce K (retrieve fewer candidates)
        if current_p95 > 500:
            actions.append("Reduce K from 20 to 10")
            self.config.update({'k': 10})

        # Action 2: Disable reranking temporarily
        if current_p95 > 800:
            actions.append("Disable reranking temporarily")
            self.config.update({'reranking_enabled': False})

        # Action 3: Fall back to cache-only mode
        if current_p95 > 1500:
            actions.append("Fallback to cache-only mode")
            self.config.update({'cache_only_mode': True})

        return actions

    def handle_availability_drop(self, current_availability):
        """
        Response to availability SLO breach
        """
        actions = []

        # Check shard health
        unhealthy = self.check_shard_health()

        if len(unhealthy) > 0:
            actions.append(f"Reroute traffic from shards: {unhealthy}")
            self.reroute_traffic(exclude_shards=unhealthy)

        # Scale up if at capacity
        if self.get_cpu_usage() > 0.8:
            actions.append("Scale up replicas")
            self.scale_replicas(target_count=self.current_replicas + 2)

        return actions
```

**Checklist**
- [ ] SLO targets defined (latency, availability, relevance)
- [ ] Metrics tracked per-query with QPS context
- [ ] Incident playbook automated (reduce K, disable rerank, fallback to cache)
- [ ] Runbook tested in staging environment

---

## Pattern 6: Upgrades & Rollbacks

### Dual-Write During Rebuild

```python
class DualIndexManager:
    """
    Manage dual indexes during upgrades
    """
    def __init__(self):
        self.primary_index = 'index-v1'
        self.shadow_index = 'index-v2'
        self.rollout_percentage = 0  # % of traffic to shadow index

    def write_dual(self, document):
        """
        Write to both indexes during migration
        """
        self.write_to_index(self.primary_index, document)
        self.write_to_index(self.shadow_index, document)

    def read_with_rollout(self, query):
        """
        Gradual rollout to new index
        """
        if random.random() < self.rollout_percentage / 100:
            # Read from shadow index
            result = self.read_from_index(self.shadow_index, query)
            result['index_version'] = self.shadow_index
            return result
        else:
            # Read from primary index
            result = self.read_from_index(self.primary_index, query)
            result['index_version'] = self.primary_index
            return result

    def increase_rollout(self, step=10):
        """
        Gradual rollout in 10% increments
        """
        self.rollout_percentage = min(100, self.rollout_percentage + step)
        log_event(f"Rollout increased to {self.rollout_percentage}%")

    def rollback(self):
        """
        Rollback to primary index
        """
        self.rollout_percentage = 0
        log_event("Rolled back to primary index")
```

### Version Tagging

```python
def tag_query_response(query_id, index_version, model_version):
    """
    Tag responses with versions for debugging
    """
    response_metadata = {
        'query_id': query_id,
        'index_version': index_version,
        'model_version': model_version,
        'timestamp': datetime.now().isoformat()
    }

    return response_metadata
```

**Checklist**
- [ ] Dual-write/dual-read during index rebuilds
- [ ] Gradual rollout (10% → 25% → 50% → 100%)
- [ ] Query/response tagged with index/model version
- [ ] Rollback path tested and rehearsed
- [ ] Metrics compared between old/new index

---

## Distributed Search SLO Checklist

- [ ] Shard/replica + failover plan documented
- [ ] Consistency model chosen and configured
- [ ] Health checks + replica lag monitoring active
- [ ] Backpressure/load shedding configured
- [ ] Multi-level caching with invalidation on index change
- [ ] Cache hit rates monitored (target: >60%)
- [ ] Relevance + latency metrics tracked with QPS
- [ ] Incident playbook automated (reduce K, disable rerank, fallback)
- [ ] Dual-index upgrades with gradual rollout
- [ ] Rollback path tested and ready
