# Health Check Patterns

Monitoring service availability for orchestration systems with liveness, readiness, and startup probes.

---

## Pattern: Health Checks

**Use when:** Monitoring service availability for orchestration systems.

**Health Check Types:**

1. **Liveness Probe** - Is the app alive?
2. **Readiness Probe** - Is the app ready to serve traffic?
3. **Startup Probe** - Has the app finished starting?

---

## Liveness Probe

**Purpose:** Determine if the app is alive (restart if not).

**Implementation:**

```javascript
app.get('/health/liveness', (req, res) => {
  // Simple: just respond (app is running)
  res.status(200).json({ status: 'alive' });
});
```

**Best Practices:**

- Keep it simple (no dependency checks)
- Fast response (<100ms)
- Don't include database or external service checks
- Use it to detect deadlocks, infinite loops, or process crashes

---

## Readiness Probe

**Purpose:** Determine if the app is ready to serve traffic (remove from load balancer if not).

**Implementation:**

```javascript
app.get('/health/readiness', async (req, res) => {
  const checks = {
    database: await checkDatabase(),
    cache: await checkRedis(),
    externalAPI: await checkExternalAPI(),
  };

  const allHealthy = Object.values(checks).every((check) => check.healthy);

  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'ready' : 'not_ready',
    checks,
  });
});

async function checkDatabase() {
  try {
    await db.raw('SELECT 1');
    return { healthy: true };
  } catch (error) {
    return { healthy: false, error: error.message };
  }
}

async function checkRedis() {
  try {
    await redis.ping();
    return { healthy: true };
  } catch (error) {
    return { healthy: false, error: error.message };
  }
}

async function checkExternalAPI() {
  try {
    const response = await fetch('https://api.example.com/health', {
      signal: AbortSignal.timeout(1000), // 1s timeout
    });
    return { healthy: response.ok };
  } catch (error) {
    return { healthy: false, error: error.message };
  }
}
```

**Best Practices:**

- Check all critical dependencies
- Fast checks (<2s total)
- Return 503 when not ready
- Include details for debugging
- Use timeouts for all checks

---

## Startup Probe

**Purpose:** Determine if the app has finished starting (slow-starting apps).

**Implementation:**

```javascript
let isReady = false;

// During startup
async function initialize() {
  await connectToDatabase();
  await warmupCache();
  await loadConfiguration();
  await preloadModels(); // ML models, etc.
  isReady = true;
}

app.get('/health/startup', (req, res) => {
  if (isReady) {
    res.status(200).json({ status: 'started' });
  } else {
    res.status(503).json({ status: 'starting' });
  }
});

// Start initialization on app launch
initialize().catch((error) => {
  console.error('Startup failed:', error);
  process.exit(1);
});
```

**Best Practices:**

- Use for slow-starting apps (>30s)
- Prevent premature restarts during initialization
- Higher failure threshold than liveness
- Disable liveness probe until startup succeeds

---

## Kubernetes Configuration

**Complete Probe Setup:**

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: app
      image: myapp:latest

      # Liveness: Restart if app is dead
      livenessProbe:
        httpGet:
          path: /health/liveness
          port: 3000
        initialDelaySeconds: 30   # Wait 30s before first check
        periodSeconds: 10          # Check every 10s
        timeoutSeconds: 1          # 1s timeout
        failureThreshold: 3        # Restart after 3 failures

      # Readiness: Remove from LB if not ready
      readinessProbe:
        httpGet:
          path: /health/readiness
          port: 3000
        initialDelaySeconds: 5     # Start checking after 5s
        periodSeconds: 5           # Check every 5s
        timeoutSeconds: 1          # 1s timeout
        failureThreshold: 3        # Mark not ready after 3 failures
        successThreshold: 1        # Mark ready after 1 success

      # Startup: Allow slow initialization
      startupProbe:
        httpGet:
          path: /health/startup
          port: 3000
        initialDelaySeconds: 0     # Start checking immediately
        periodSeconds: 5           # Check every 5s
        timeoutSeconds: 1          # 1s timeout
        failureThreshold: 30       # Allow 150s startup (30 * 5s)
```

---

## Advanced Health Checks

**Shallow vs Deep Checks:**

```javascript
// Shallow: fast, minimal dependencies
app.get('/health', async (req, res) => {
  const isHealthy = await quickHealthCheck();
  res.status(isHealthy ? 200 : 503).json({ status: isHealthy ? 'healthy' : 'unhealthy' });
});

// Deep: comprehensive, slower
app.get('/health/deep', async (req, res) => {
  const checks = {
    database: await checkDatabaseConnection(),
    databasePerformance: await checkDatabaseQueryTime(),
    cache: await checkRedis(),
    disk: await checkDiskSpace(),
    memory: await checkMemoryUsage(),
    dependencies: await checkAllDependencies(),
  };

  const allHealthy = Object.values(checks).every((c) => c.healthy);

  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'healthy' : 'unhealthy',
    checks,
    timestamp: new Date().toISOString(),
  });
});

async function checkDatabaseQueryTime() {
  const start = Date.now();
  try {
    await db.raw('SELECT 1');
    const duration = Date.now() - start;
    return {
      healthy: duration < 100, // <100ms is healthy
      duration,
    };
  } catch (error) {
    return { healthy: false, error: error.message };
  }
}

async function checkDiskSpace() {
  const disk = await getDiskUsage();
  return {
    healthy: disk.percentUsed < 90,
    percentUsed: disk.percentUsed,
    available: disk.available,
  };
}

async function checkMemoryUsage() {
  const memUsage = process.memoryUsage();
  const percentUsed = (memUsage.heapUsed / memUsage.heapTotal) * 100;
  return {
    healthy: percentUsed < 90,
    percentUsed,
    heapUsed: memUsage.heapUsed,
    heapTotal: memUsage.heapTotal,
  };
}
```

---

## Dependency Health Checks

**Aggregate Dependencies:**

```javascript
const dependencies = [
  { name: 'database', check: checkDatabase, critical: true },
  { name: 'cache', check: checkRedis, critical: true },
  { name: 'email', check: checkEmailService, critical: false },
  { name: 'analytics', check: checkAnalytics, critical: false },
];

app.get('/health/readiness', async (req, res) => {
  const results = await Promise.allSettled(
    dependencies.map(async (dep) => ({
      name: dep.name,
      critical: dep.critical,
      result: await dep.check(),
    }))
  );

  const checks = {};
  let criticalFailure = false;

  results.forEach((result, i) => {
    const dep = dependencies[i];
    if (result.status === 'fulfilled') {
      checks[dep.name] = result.value.result;
      if (dep.critical && !result.value.result.healthy) {
        criticalFailure = true;
      }
    } else {
      checks[dep.name] = { healthy: false, error: result.reason.message };
      if (dep.critical) {
        criticalFailure = true;
      }
    }
  });

  res.status(criticalFailure ? 503 : 200).json({
    status: criticalFailure ? 'not_ready' : 'ready',
    checks,
  });
});
```

---

## Health Check Security

**Prevent Abuse:**

```javascript
const rateLimit = require('express-rate-limit');

const healthCheckLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 60, // 60 requests per minute
  message: 'Too many health check requests',
});

app.get('/health', healthCheckLimiter, async (req, res) => {
  // Health check logic
});

// Don't require auth for health checks (load balancers need access)
// But log suspicious patterns
app.use('/health', (req, res, next) => {
  const userAgent = req.headers['user-agent'];
  if (!userAgent || !userAgent.includes('kube-probe')) {
    logger.warn('Health check from non-k8s source', {
      ip: req.ip,
      userAgent,
    });
  }
  next();
});
```

---

## Monitoring Health Checks

**Metrics:**

```javascript
app.get('/health/readiness', async (req, res) => {
  const startTime = Date.now();
  const checks = await performHealthChecks();
  const duration = Date.now() - startTime;

  const allHealthy = Object.values(checks).every((c) => c.healthy);

  // Record metrics
  metrics.histogram('health_check.duration', duration);
  metrics.gauge('health_check.status', allHealthy ? 1 : 0);

  Object.entries(checks).forEach(([name, check]) => {
    metrics.gauge(`health_check.dependency.${name}`, check.healthy ? 1 : 0);
  });

  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'ready' : 'not_ready',
    checks,
    duration,
  });
});
```

---

## Checklist

- [ ] Liveness probe checks app is alive (simple check)
- [ ] Readiness probe checks dependencies (database, cache, APIs)
- [ ] Startup probe for slow-starting apps
- [ ] Health checks timeout quickly (1-2s)
- [ ] Failed health checks logged
- [ ] Health check endpoints don't require auth
- [ ] Health checks don't overload dependencies
- [ ] Critical vs non-critical dependencies differentiated
- [ ] Health check metrics tracked
- [ ] Rate limiting prevents abuse

---

## Related Resources

- [graceful-degradation.md](graceful-degradation.md) - Handle failed health checks gracefully
- [timeout-policies.md](timeout-policies.md) - Configure health check timeouts
- [resilience-checklists.md](resilience-checklists.md) - Health and readiness checklist
