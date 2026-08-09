# Open WebUI Deployment Recipe

Runnable end-to-end recipe for deploying Open WebUI as a team-facing chat interface over a local or self-hosted Ollama backend.

Tested on: Docker 25+, macOS 14+, Ubuntu 22.04/24.04. Last updated: 2026-04.

---

## 1. Prerequisites

- Docker installed and running (`docker --version`)
- Ollama running on the same host or accessible network address
- If using Ollama on the same host, note the internal Docker network address (see step 3)

---

## 2. Quick start (single container, local Ollama)

```bash
docker run -d \
  --name open-webui \
  -p 3000:8080 \
  -v open-webui-data:/app/backend/data \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  --add-host=host.docker.internal:host-gateway \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main
```

Open `http://localhost:3000` in a browser. Create an admin account on first visit.

---

## 3. Ollama URL by platform

| Platform | URL to use |
|----------|-----------|
| macOS (Docker Desktop) | `http://host.docker.internal:11434` |
| Linux (Docker Engine) | `http://172.17.0.1:11434` or use `--network=host` |
| Remote host | `http://<ollama-host-ip>:11434` |
| Same Compose network | `http://ollama:11434` (see step 4) |

---

## 4. Docker Compose (recommended for teams)

```yaml
# docker-compose.yml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ollama-models:/root/.ollama
    ports:
      - "11434:11434"
    restart: unless-stopped
    # Uncomment for NVIDIA GPU:
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: all
    #           capabilities: [gpu]

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    depends_on:
      - ollama
    ports:
      - "3000:8080"
    volumes:
      - open-webui-data:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY:-change-me-in-production}
    restart: unless-stopped

volumes:
  ollama-models:
  open-webui-data:
```

```bash
# Start
docker compose up -d

# Pull a model into the running Ollama container
docker exec ollama ollama pull llama3.1:8b-instruct-q4_K_M

# Tail logs
docker compose logs -f open-webui
```

---

## 5. Environment variables (key settings)

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint |
| `WEBUI_SECRET_KEY` | random | Session signing key — set a stable value |
| `WEBUI_AUTH` | `true` | Require login; set `false` only on completely private networks |
| `DEFAULT_MODELS` | (all) | Comma-separated model IDs to show by default |
| `ENABLE_SIGNUP` | `true` | Allow new user self-registration |
| `DEFAULT_USER_ROLE` | `pending` | Role assigned to new signups: `pending`, `user`, `admin` |
| `OPENAI_API_KEY` | — | Pass-through to OpenAI API (optional; enables cloud models in UI) |
| `OPENAI_API_BASE_URL` | `https://api.openai.com/v1` | Override for any OpenAI-compatible backend |

See the full list at https://docs.openwebui.com/getting-started/env-configuration

---

## 6. Add OpenAI-compatible backends alongside Ollama

Open WebUI can proxy multiple backends simultaneously:

```bash
# In UI: Admin Panel → Settings → Connections
# Add a new OpenAI connection:
#   URL:     http://another-host:8000/v1
#   API Key: (your key or leave blank for local)
```

Or via environment variables for a second endpoint:

```yaml
environment:
  - OLLAMA_BASE_URL=http://ollama:11434
  - OPENAI_API_KEY=sk-...
  - OPENAI_API_BASE_URL=https://api.openai.com/v1
```

---

## 7. HTTPS / reverse proxy (production)

Never expose Open WebUI on port 80 or 3000 to the internet without TLS.

**Caddy (recommended — auto TLS):**
```caddyfile
# Caddyfile
ai.yourdomain.com {
    reverse_proxy open-webui:8080
    basicauth /* {
        # caddy hash-password to generate hashes
        admin $2a$14$...
    }
}
```

**Nginx:**
```nginx
server {
    listen 443 ssl;
    server_name ai.yourdomain.com;
    ssl_certificate     /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass         http://localhost:3000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
    }
}
```

---

## 8. Upgrade

```bash
docker compose pull
docker compose up -d
```

Data volume (`open-webui-data`) persists across upgrades.

---

## 9. Backup

```bash
# Stop, copy volume, restart
docker compose stop open-webui
docker run --rm -v open-webui-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/open-webui-backup-$(date +%Y%m%d).tar.gz /data
docker compose start open-webui
```

---

## Known Traps

- Not setting `WEBUI_SECRET_KEY` — sessions invalidate on container restart.
- Leaving `ENABLE_SIGNUP=true` on an internet-facing deployment — anyone can register.
- Using `:main` tag in production — pin to a specific release tag (e.g. `:v0.5.x`).
- Exposing the Ollama port (11434) directly — Open WebUI should be the only entry point for users.
- Forgetting to pull models before team demo — `docker exec ollama ollama pull <model>`.
- Not backing up the data volume before upgrading.
