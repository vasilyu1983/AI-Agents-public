# Ollama Setup Recipe

Runnable end-to-end recipe for installing and operating Ollama locally or on a small server.

Tested on: macOS 14+, Ubuntu 22.04/24.04, WSL2 (Windows 11). Last updated: 2026-04.

---

## 1. Install

**macOS:**
```bash
# Homebrew
brew install ollama

# Or direct download (installs to /usr/local/bin)
curl -fsSL https://ollama.com/install.sh | sh
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://ollama.com/install.sh | sh
# Starts systemd service automatically
```

**Verify:**
```bash
ollama --version
```

---

## 2. Start the server

```bash
# macOS: launches automatically after install, or run manually
ollama serve

# Linux: managed by systemd
sudo systemctl status ollama
sudo systemctl start ollama   # if not running
```

Default endpoint: `http://localhost:11434`

---

## 3. Pull a model

```bash
# Recommended starting models
ollama pull llama3.2:3b            # fast, fits in <4 GB RAM
ollama pull llama3.1:8b            # general-purpose
ollama pull qwen3:8b               # strong at instruction following
ollama pull mistral:7b-instruct    # lean, fast

# Check what's pulled
ollama list
```

Model files are stored in `~/.ollama/models/` on macOS/Linux.

---

## 4. Run interactively

```bash
ollama run llama3.1:8b
# Type your prompt; /bye to exit
```

---

## 5. Use the OpenAI-compatible API

Ollama exposes an OpenAI-compatible endpoint at `/v1/chat/completions`.

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "What is 2+2?"}],
    "max_tokens": 64
  }'
```

**Python (no sdk required):**
```python
import urllib.request, json

payload = json.dumps({
    "model": "llama3.1:8b",
    "messages": [{"role": "user", "content": "Say hello."}],
    "max_tokens": 32,
}).encode()

req = urllib.request.Request(
    "http://localhost:11434/v1/chat/completions",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req) as resp:
    print(json.loads(resp.read()))
```

**With the openai Python SDK:**
```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
resp = client.chat.completions.create(
    model="llama3.1:8b",
    messages=[{"role": "user", "content": "What is 2+2?"}],
)
print(resp.choices[0].message.content)
```

---

## 6. Pin model versions and quantization

Always pin to explicit tag + quant level in production-adjacent workflows:

```bash
ollama pull llama3.1:8b-instruct-q4_K_M
ollama pull qwen3:8b-q5_K_M
```

**List available quant levels for a model:**
```bash
# Check Ollama model page: https://ollama.com/library/<model>
# Or pull the specific tag directly:
ollama pull llama3.1:8b-instruct-q4_K_M
```

Set a custom Modelfile to pin system prompt and parameters:

```Dockerfile
# Modelfile
FROM llama3.1:8b-instruct-q4_K_M

SYSTEM "You are a helpful assistant. Be concise."

PARAMETER temperature 0.7
PARAMETER top_k 40
PARAMETER num_ctx 4096
```

```bash
ollama create my-assistant -f ./Modelfile
ollama run my-assistant
```

---

## 7. Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `0.0.0.0:11434` | Bind address |
| `OLLAMA_MODELS` | `~/.ollama/models` | Model storage path |
| `OLLAMA_NUM_PARALLEL` | 1 | Concurrent request limit |
| `OLLAMA_MAX_LOADED_MODELS` | 1 | Models kept in memory |
| `OLLAMA_KEEP_ALIVE` | `5m` | Time to keep model in memory after last request |
| `OLLAMA_GPU_OVERHEAD` | 0 | Reserved VRAM bytes |

Set in shell or `/etc/systemd/system/ollama.service.d/override.conf` on Linux.

---

## 8. GPU setup

**macOS:** Metal is used automatically on Apple Silicon and AMD GPUs.

**Linux NVIDIA:**
```bash
# Verify CUDA is installed
nvidia-smi
# Ollama detects CUDA automatically; no extra config needed
```

**Linux AMD (ROCm):**
```bash
# Install ROCm, then use the ROCm-enabled Ollama build
# See https://ollama.com/download/linux
```

---

## 9. Expose to a local network (team use)

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

Add a reverse proxy (nginx/caddy) with basic auth before exposing beyond localhost:

```nginx
# Minimal nginx config — add SSL and auth in production
server {
    listen 443 ssl;
    server_name ollama.internal;
    location / {
        proxy_pass http://127.0.0.1:11434;
        auth_basic "Ollama";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
```

Never expose Ollama directly to the internet without auth and TLS.

---

## 10. Validate with latency_benchmark.py

After setup, verify throughput:

```bash
python ../../scripts/latency_benchmark.py \
  --endpoint http://localhost:11434/v1 \
  --model llama3.1:8b \
  --requests 20 --concurrency 2
```

(Script lives in `ai-llm-inference/scripts/latency_benchmark.py`.)

---

## Known Traps

- Using `latest` tag — breaks reproducibility when Ollama updates the default version.
- Running Ollama without VRAM headroom — KV cache OOM causes silent hangs or errors.
- Exposing port 11434 to the internet — no auth by default.
- Setting `OLLAMA_NUM_PARALLEL > 1` on consumer hardware without checking peak VRAM.
- Forgetting `OLLAMA_KEEP_ALIVE=0` in memory-constrained environments — model stays loaded permanently by default.
