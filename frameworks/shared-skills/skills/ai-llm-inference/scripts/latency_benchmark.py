#!/usr/bin/env python3
"""
latency_benchmark.py — Latency benchmark for OpenAI-compatible inference endpoints.

Issues N concurrent requests against a /v1/chat/completions endpoint and reports
p50/p95/p99 latencies and throughput. Uses stdlib urllib + threading only.

Usage:
    python latency_benchmark.py --endpoint http://localhost:11434/v1 --model llama3
    python latency_benchmark.py --endpoint https://api.openai.com/v1 --model gpt-4o-mini \\
        --requests 50 --concurrency 10 --api-key $OPENAI_API_KEY
    python latency_benchmark.py --endpoint http://localhost:8000/v1 --model mistral \\
        --prompt "What is the capital of France?" --output results.json
    python latency_benchmark.py --help

Environment variables:
    OPENAI_API_KEY  — used if --api-key is not provided

Output:
    Console summary table + optional JSON file with all per-request timings.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import NamedTuple


class RequestResult(NamedTuple):
    index: int
    latency_s: float
    status: int  # 200 = success, negative = network/timeout error
    tokens_generated: int
    error: str


def _do_request(
    index: int,
    url: str,
    headers: dict,
    body: bytes,
    timeout: float,
) -> RequestResult:
    t0 = time.perf_counter()
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            elapsed = time.perf_counter() - t0
            try:
                data = json.loads(raw)
                tokens = data.get("usage", {}).get("completion_tokens", 0)
            except Exception:
                tokens = 0
            return RequestResult(index, elapsed, resp.status, tokens, "")
    except urllib.error.HTTPError as e:
        elapsed = time.perf_counter() - t0
        return RequestResult(index, elapsed, e.code, 0, str(e))
    except Exception as e:
        elapsed = time.perf_counter() - t0
        return RequestResult(index, elapsed, -1, 0, str(e))


def percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(sorted_values) - 1)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (k - lo)


def run(
    endpoint: str,
    model: str,
    prompt: str,
    n_requests: int,
    concurrency: int,
    api_key: str | None,
    max_tokens: int,
    timeout: float,
    output_path: Path | None,
) -> int:
    url = endpoint.rstrip("/") + "/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "stream": False,
    }).encode()

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    print(f"Endpoint : {url}")
    print(f"Model    : {model}")
    print(f"Requests : {n_requests}  Concurrency: {concurrency}  Max-tokens: {max_tokens}")
    print(f"Prompt   : {repr(prompt[:80])}")
    print()

    results: list[RequestResult] = []
    wall_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {
            pool.submit(_do_request, i, url, headers, payload, timeout): i
            for i in range(n_requests)
        }
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            status_str = f"HTTP {r.status}" if r.status > 0 else f"ERR({r.error[:40]})"
            print(f"  [{r.index:04d}] {r.latency_s*1000:8.1f} ms  {status_str}", end="\r")

    wall_elapsed = time.perf_counter() - wall_start
    print(" " * 80, end="\r")  # clear progress line

    successes = [r for r in results if r.status == 200]
    failures = [r for r in results if r.status != 200]

    if not successes:
        print("[ERROR] All requests failed.", file=sys.stderr)
        for r in failures[:5]:
            print(f"  status={r.status} error={r.error}", file=sys.stderr)
        return 1

    latencies = sorted(r.latency_s for r in successes)
    mean_lat = sum(latencies) / len(latencies)
    throughput = len(successes) / wall_elapsed
    total_tokens = sum(r.tokens_generated for r in successes)
    tok_per_sec = total_tokens / wall_elapsed if total_tokens > 0 else 0

    summary = {
        "endpoint": url,
        "model": model,
        "total_requests": n_requests,
        "successful": len(successes),
        "failed": len(failures),
        "wall_time_s": round(wall_elapsed, 3),
        "throughput_rps": round(throughput, 3),
        "tokens_per_sec": round(tok_per_sec, 1),
        "latency_ms": {
            "mean": round(mean_lat * 1000, 1),
            "p50": round(percentile(latencies, 50) * 1000, 1),
            "p95": round(percentile(latencies, 95) * 1000, 1),
            "p99": round(percentile(latencies, 99) * 1000, 1),
            "min": round(latencies[0] * 1000, 1),
            "max": round(latencies[-1] * 1000, 1),
        },
    }

    print(f"\n{'='*50}")
    print(f"Successful   : {summary['successful']}/{summary['total_requests']}")
    print(f"Wall time    : {summary['wall_time_s']:.2f}s")
    print(f"Throughput   : {summary['throughput_rps']:.2f} req/s")
    if total_tokens > 0:
        print(f"Tok/sec      : {summary['tokens_per_sec']:.1f}")
    print(f"\nLatency (ms) :")
    lm = summary["latency_ms"]
    print(f"  mean={lm['mean']:.1f}  p50={lm['p50']:.1f}  p95={lm['p95']:.1f}  p99={lm['p99']:.1f}")
    print(f"  min={lm['min']:.1f}  max={lm['max']:.1f}")
    if failures:
        print(f"\nFailed requests: {len(failures)}")

    if output_path:
        full_report = {
            **summary,
            "per_request": [
                {
                    "index": r.index,
                    "latency_ms": round(r.latency_s * 1000, 2),
                    "status": r.status,
                    "tokens": r.tokens_generated,
                    "error": r.error,
                }
                for r in sorted(results, key=lambda x: x.index)
            ],
        }
        with output_path.open("w") as f:
            json.dump(full_report, f, indent=2)
        print(f"\nFull report: {output_path}")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Latency benchmark for OpenAI-compatible inference endpoints.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--endpoint", required=True, help="Base URL, e.g. http://localhost:11434/v1")
    parser.add_argument("--model", required=True, help="Model ID to pass in the request body")
    parser.add_argument("--prompt", default="Say hello in one word.", help="Prompt text")
    parser.add_argument("--requests", type=int, default=20, dest="n_requests", help="Total requests (default: 20)")
    parser.add_argument("--concurrency", type=int, default=5, help="Concurrent workers (default: 5)")
    parser.add_argument("--max-tokens", type=int, default=64, help="max_tokens per request (default: 64)")
    parser.add_argument("--timeout", type=float, default=60.0, help="Per-request timeout seconds (default: 60)")
    parser.add_argument("--api-key", default=None, help="Bearer token (falls back to OPENAI_API_KEY env var)")
    parser.add_argument("--output", type=Path, default=None, help="Write JSON report to file")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")

    sys.exit(run(
        endpoint=args.endpoint,
        model=args.model,
        prompt=args.prompt,
        n_requests=args.n_requests,
        concurrency=args.concurrency,
        api_key=api_key,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
        output_path=args.output,
    ))


if __name__ == "__main__":
    main()
