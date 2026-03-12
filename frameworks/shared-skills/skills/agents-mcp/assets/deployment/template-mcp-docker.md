# MCP Docker Deployment Template

*Purpose: Production-ready Docker configuration for deploying MCP servers.*

---

## When to Use

Use this template when:

- Deploying MCP servers to production
- Running MCP servers in containers
- Setting up CI/CD pipelines
- Deploying to Kubernetes or cloud platforms
- Standardizing development environments

---

# TEMPLATE STARTS HERE

## 1. Project Overview

**Project Name:**
[mcp-server-name]

**Deployment Target:**
- [ ] Local Docker
- [ ] Docker Compose
- [ ] Kubernetes
- [ ] AWS ECS/Fargate
- [ ] Google Cloud Run
- [ ] Azure Container Apps

---

## 2. Dockerfile

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY src/ ./src/

# Build TypeScript
RUN npm run build

# Prune dev dependencies
RUN npm prune --production

# Production stage
FROM node:20-alpine AS production

# Security: Run as non-root user
RUN addgroup -g 1001 -S mcp && \
    adduser -u 1001 -S mcp -G mcp

WORKDIR /app

# Copy built files
COPY --from=builder --chown=mcp:mcp /app/dist ./dist
COPY --from=builder --chown=mcp:mcp /app/node_modules ./node_modules
COPY --from=builder --chown=mcp:mcp /app/package.json ./

# Set environment
ENV NODE_ENV=production

# Switch to non-root user
USER mcp

# Health check (for HTTP transport)
# HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
#   CMD wget --no-verbose --tries=1 --spider http://localhost:3001/health || exit 1

# Start server
CMD ["node", "dist/index.js"]
```

---

## 3. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  mcp-server:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: [mcp-server-name]
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      # Database (if needed)
      - DATABASE_URL=${DATABASE_URL}
      # API (if needed)
      - API_BASE_URL=${API_BASE_URL}
      - API_KEY=${API_KEY}
      # Filesystem (if needed)
      - ALLOWED_PATHS=/data
    volumes:
      # Mount data directory (for filesystem MCP)
      - ./data:/data:ro
      # Mount logs
      - ./logs:/app/logs
    # For stdio transport (local development)
    stdin_open: true
    tty: true
    # For HTTP transport (production)
    # ports:
    #   - "3001:3001"
    networks:
      - mcp-network
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  # Optional: Database
  postgres:
    image: postgres:15-alpine
    container_name: mcp-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=${POSTGRES_USER:-mcp}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB:-mcp}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - mcp-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-mcp}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Optional: Redis (for rate limiting/caching)
  redis:
    image: redis:7-alpine
    container_name: mcp-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - mcp-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:

networks:
  mcp-network:
    driver: bridge
```

---

## 4. Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mcp-server:
    image: ${REGISTRY}/${IMAGE_NAME}:${VERSION}
    restart: always
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      rollback_config:
        parallelism: 1
        delay: 10s
    environment:
      - NODE_ENV=production
    env_file:
      - .env.production
    # For HTTP transport with load balancing
    ports:
      - "3001:3001"
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: json-file
      options:
        max-size: "50m"
        max-file: "5"
    secrets:
      - db_password
      - api_key

secrets:
  db_password:
    external: true
  api_key:
    external: true
```

---

## 5. Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: [mcp-server-name]
  labels:
    app: [mcp-server-name]
spec:
  replicas: 2
  selector:
    matchLabels:
      app: [mcp-server-name]
  template:
    metadata:
      labels:
        app: [mcp-server-name]
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
        - name: mcp-server
          image: ${REGISTRY}/${IMAGE_NAME}:${VERSION}
          ports:
            - containerPort: 3001
          env:
            - name: NODE_ENV
              value: "production"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: mcp-secrets
                  key: database-url
            - name: API_KEY
              valueFrom:
                secretKeyRef:
                  name: mcp-secrets
                  key: api-key
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          livenessProbe:
            httpGet:
              path: /health
              port: 3001
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 3001
            initialDelaySeconds: 5
            periodSeconds: 5
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: logs
              mountPath: /app/logs
      volumes:
        - name: tmp
          emptyDir: {}
        - name: logs
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: [mcp-server-name]
spec:
  selector:
    app: [mcp-server-name]
  ports:
    - port: 3001
      targetPort: 3001
  type: ClusterIP
---
apiVersion: v1
kind: Secret
metadata:
  name: mcp-secrets
type: Opaque
stringData:
  database-url: "[DATABASE_URL]"
  api-key: "[API_KEY]"
```

---

## 6. CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy MCP Server

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production

    steps:
      - name: Deploy to Kubernetes
        uses: azure/k8s-deploy@v4
        with:
          manifests: |
            k8s/deployment.yaml
          images: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
```

---

## 7. Health Check Endpoint (for HTTP transport)

```typescript
// src/health.ts
import express from 'express';

export function addHealthChecks(app: express.Application) {
  // Liveness probe - is the server running?
  app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok' });
  });

  // Readiness probe - is the server ready to accept requests?
  app.get('/ready', async (req, res) => {
    try {
      // Check database connection
      await pool.query('SELECT 1');
      res.status(200).json({ status: 'ready' });
    } catch (error) {
      res.status(503).json({ status: 'not ready', error: (error as Error).message });
    }
  });

  // Metrics endpoint (optional)
  app.get('/metrics', (req, res) => {
    res.set('Content-Type', 'text/plain');
    res.send(`
# HELP mcp_requests_total Total number of MCP requests
# TYPE mcp_requests_total counter
mcp_requests_total{tool="query_database"} ${metrics.queryCount}
mcp_requests_total{tool="list_tables"} ${metrics.listCount}

# HELP mcp_request_duration_seconds Request duration in seconds
# TYPE mcp_request_duration_seconds histogram
mcp_request_duration_seconds_bucket{le="0.1"} ${metrics.durationBuckets['0.1']}
mcp_request_duration_seconds_bucket{le="0.5"} ${metrics.durationBuckets['0.5']}
mcp_request_duration_seconds_bucket{le="1.0"} ${metrics.durationBuckets['1.0']}
    `.trim());
  });
}
```

---

## 8. Environment Files

```bash
# .env.example
NODE_ENV=development
LOG_LEVEL=debug

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mcp

# API
API_BASE_URL=https://api.example.com
API_KEY=your-api-key

# Security
ALLOWED_PATHS=/workspace
```

```bash
# .env.production (DO NOT COMMIT)
NODE_ENV=production
LOG_LEVEL=info

# Use secrets manager references
DATABASE_URL=${DATABASE_URL}
API_KEY=${API_KEY}
```

---

## 9. Build and Deploy Commands

```bash
# Local development
docker compose up -d

# Build for production
docker build -t [mcp-server-name]:latest .

# Push to registry
docker tag [mcp-server-name]:latest ghcr.io/[org]/[mcp-server-name]:latest
docker push ghcr.io/[org]/[mcp-server-name]:latest

# Deploy to Kubernetes
kubectl apply -f k8s/

# Check deployment
kubectl get pods -l app=[mcp-server-name]
kubectl logs -l app=[mcp-server-name] -f

# Scale
kubectl scale deployment [mcp-server-name] --replicas=3
```

---

## 10. Security Checklist

```text
[ ] Run as non-root user in container
[ ] Read-only root filesystem where possible
[ ] No sensitive data in Dockerfile or image
[ ] Secrets managed via Kubernetes Secrets or secrets manager
[ ] Container image scanned for vulnerabilities
[ ] Network policies restrict pod communication
[ ] Resource limits set (CPU, memory)
[ ] Health checks configured
[ ] Logging to stdout/stderr (not files)
[ ] TLS enabled for HTTP transport
[ ] OAuth 2.1 configured for production HTTP
```

---

## 11. Troubleshooting

```bash
# Check container logs
docker logs [container-name] -f

# Shell into container
docker exec -it [container-name] /bin/sh

# Check resource usage
docker stats [container-name]

# Kubernetes debugging
kubectl describe pod [pod-name]
kubectl logs [pod-name] --previous
kubectl exec -it [pod-name] -- /bin/sh
```
