# Ollama Setup Recipe

Runnable end-to-end recipe for installing and operating Ollama locally or on a small server.

Tested on: macOS 14+, Ubuntu 22.04/24.04, WSL2 (Windows 11). Defaults and flags change between Ollama releases — confirm them with `ollama serve --help` and the Ollama FAQ (in https://github.com/ollama/ollama/tree/main/docs) before relying on them.

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

Default endpoint: `http://localhost:11434` — by default Ollama binds to loopback (`127.0.0.1`) only, so nothing else on the network can reach it.

---

## 3. Pull a model

Model tags below are examples. Pick the current model from https://ollama.com/library, size it with `references/model-sizing-matrix.md`, and pin the exact tag you tested.

```bash
# Example starting models
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
    model="<model-tag>",  # a tag you've pulled with `ollama pull`
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

Lookup step: run `ollama serve --help` (it lists the supported environment variables) and read the Ollama FAQ for current defaults. The values below are the documented defaults at the time of writing; re-check them after an upgrade.

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `127.0.0.1:11434` | Bind address. Loopback only by default; `0.0.0.0` exposes the unauthenticated API on every interface (see step 9) |
| `OLLAMA_MODELS` | `~/.ollama/models` | Model storage path |
| `OLLAMA_NUM_PARALLEL` | 1 | Concurrent request limit |
| `OLLAMA_MAX_LOADED_MODELS` | 3 × number of GPUs (3 on CPU-only) | Models kept in memory at once, if they fit |
| `OLLAMA_KEEP_ALIVE` | `5m` | Time to keep a model in memory after its last request; `0` unloads immediately |
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

The Ollama API has no authentication. Exposing it is an explicit decision, not a default:

- **Preferred:** leave `OLLAMA_HOST` on loopback and run an authenticating reverse proxy (nginx/caddy with TLS + auth) on the same host; the proxy talks to `127.0.0.1:11434`.
- **Only if the proxy or client runs on another host/container:** bind `OLLAMA_HOST=0.0.0.0:11434`, and firewall port 11434 so only the proxy (or a VPN range) can reach it.
- Never publish the raw API to the internet or to an untrusted network.

```bash
# Only when a separate host/container must reach Ollama — and only behind a firewall rule for 11434
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

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
- Exposing port 11434 to the internet — the API has no auth.
- Setting `OLLAMA_HOST=0.0.0.0` "to make it work" — the default loopback bind is the safe one; changing it exposes the API to the whole network unless a firewall or proxy fronts it.
- Setting `OLLAMA_NUM_PARALLEL > 1` on consumer hardware without checking peak VRAM.
- Ignoring `OLLAMA_KEEP_ALIVE` — by default a model stays loaded for 5 minutes after its last request. Set `0` in memory-constrained environments to unload immediately, or a longer value to avoid reload latency on a dedicated box.
- Assuming only one model is resident — several models can stay loaded at once (see `OLLAMA_MAX_LOADED_MODELS`); cap it when VRAM is tight.
