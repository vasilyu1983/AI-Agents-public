"""CLI regression tests for caller-supplied pricing validation."""

import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path


SCRIPT = Path(__file__).with_name("cost_estimator.py")


def test_nonfinite_price_rejected_before_estimate(tmp_path):
    # The bad row is filtered out by --providers, so no estimate is ever computed for it:
    # only the load-time check can reject it. A corrupt file must not price the other rows.
    prices = tmp_path / "prices.json"
    for value in ("1e309", "NaN", "Infinity", "-Infinity"):
        prices.write_text(
            '{"checked":"2026-01-01","models":{'
            '"other/bad":{"input_per_1m":' + value + ',"output_per_1m":1},'
            '"vendor/model":{"input_per_1m":2,"output_per_1m":4}}}',
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--prices", str(prices),
             "--input-tokens", "100", "--output-tokens", "100", "--json",
             "--providers", "vendor"],
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == 2, (value, result.stdout, result.stderr)
        assert not result.stdout
        assert "finite" in result.stderr.lower()


def test_finite_price_still_estimates(tmp_path):
    prices = tmp_path / "prices.json"
    prices.write_text(json.dumps({
        "checked": "2026-01-01", "models": {
            "vendor/model": {"input_per_1m": 2, "output_per_1m": 4},
        },
    }), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--prices", str(prices),
         "--input-tokens", "1000000", "--output-tokens", "1000000", "--json"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["estimates"][0]["total_cost_usd"] == 6


def test_finite_rates_with_overflowing_estimate_fail_closed(tmp_path):
    prices = tmp_path / "prices.json"
    prices.write_text(json.dumps({
        "checked": "2026-01-01", "models": {
            "vendor/model": {"input_per_1m": 1e308, "output_per_1m": 1},
        },
    }), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--prices", str(prices),
         "--input-tokens", "2000000", "--output-tokens", "100", "--json"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 2, result.stdout
    assert not result.stdout
    assert "finite" in result.stderr.lower()


def _valid_prices(tmp_path):
    prices = tmp_path / "prices.json"
    prices.write_text(json.dumps({
        "checked": "2026-01-01", "models": {
            "vendor/model": {"input_per_1m": 2, "output_per_1m": 4},
        },
    }), encoding="utf-8")
    return prices


def _estimate(flag, path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), flag, str(path),
         "--input-tokens", "1000000", "--output-tokens", "1000000", "--json"],
        capture_output=True, text=True, check=False,
    )


def test_pricing_flag_and_prices_alias_both_estimate(tmp_path):
    prices = _valid_prices(tmp_path)
    for flag in ("--pricing", "--prices"):
        result = _estimate(flag, prices)
        assert result.returncode == 0, (flag, result.stderr)
        assert json.loads(result.stdout)["estimates"][0]["total_cost_usd"] == 6


def test_unreadable_price_file_exits_2_naming_the_file(tmp_path):
    not_utf8 = tmp_path / "latin1.json"
    not_utf8.write_bytes(b'{"checked":"2026-01-01","source":"caf\xe9"}')
    for path in (tmp_path, not_utf8):
        # The alias isolates the loader check from the flag rename.
        result = _estimate("--prices", path)
        assert result.returncode == 2, (path, result.stdout, result.stderr)
        assert not result.stdout
        assert "Traceback" not in result.stderr
        assert str(path) in result.stderr


def test_oversized_integer_price_exits_2_naming_the_file(tmp_path):
    # json.loads raises plain ValueError past the int-string digit limit.
    prices = tmp_path / "huge.json"
    prices.write_text('{"checked":"2026-01-01","models":{"vendor/model":'
                      '{"input_per_1m":' + "1" * 5000 + ',"output_per_1m":1}}}',
                      encoding="utf-8")
    result = _estimate("--prices", prices)
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert "Traceback" not in result.stderr
    assert str(prices) in result.stderr


def test_unreadable_prompt_file_exits_2_naming_the_file(tmp_path):
    prices = _valid_prices(tmp_path)
    prompt_dir = tmp_path / "prompt_dir"
    prompt_dir.mkdir()
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--prices", str(prices),
         "--prompt-file", str(prompt_dir), "--output-tokens", "10"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert "Traceback" not in result.stderr
    assert str(prompt_dir) in result.stderr


def _run(prices, *extra):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--pricing", str(prices), "--json", *extra],
        capture_output=True, text=True, check=False,
    )


def _write_prices(tmp_path, checked):
    prices = tmp_path / "prices.json"
    prices.write_text(json.dumps({
        "checked": checked.isoformat(), "models": {
            "vendor/model": {"input_per_1m": 2, "output_per_1m": 4},
        },
    }), encoding="utf-8")
    return prices


def test_nonpositive_tokens_exit_2(tmp_path):
    # A zero or negative count would print a zero or negative cost as a valid estimate.
    prices = _valid_prices(tmp_path)
    for tokens in (("0", "10"), ("-5", "10"), ("10", "0")):
        result = _run(prices, "--input-tokens", tokens[0], "--output-tokens", tokens[1])
        assert result.returncode == 2, (tokens, result.stdout, result.stderr)
        assert not result.stdout
        assert "must be > 0" in result.stderr


def test_future_checked_date_exits_2(tmp_path):
    # A future date is a typo; accepting it would report stale prices as fresh.
    prices = _write_prices(tmp_path, date.today() + timedelta(days=1))
    result = _run(prices, "--input-tokens", "10", "--output-tokens", "10")
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert not result.stdout
    assert "in the future" in result.stderr


def test_overflowing_token_count_exits_2_without_traceback(tmp_path):
    # int / 1_000_000 raises OverflowError for a huge count; it must not escape as a crash.
    prices = _valid_prices(tmp_path)
    result = _run(prices, "--input-tokens", "9" * 400, "--output-tokens", "10")
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert not result.stdout
    assert "Traceback" not in result.stderr
    assert "not finite" in result.stderr


def test_duplicate_model_exits_2_naming_the_model(tmp_path):
    # json.loads keeps the last duplicate, so a copy-pasted row would silently reprice the model.
    prices = tmp_path / "dup.json"
    prices.write_text(
        '{"checked":"2026-01-01","models":{'
        '"vendor/dup-model":{"input_per_1m":2,"output_per_1m":4},'
        '"vendor/dup-model":{"input_per_1m":200,"output_per_1m":400}}}',
        encoding="utf-8",
    )
    result = _run(prices, "--input-tokens", "10", "--output-tokens", "10")
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert not result.stdout
    assert "Traceback" not in result.stderr
    assert "vendor/dup-model" in result.stderr
    assert "duplicate" in result.stderr


def test_max_age_days_rejects_stale_prices_only_when_set(tmp_path):
    prices = _write_prices(tmp_path, date.today() - timedelta(days=30))
    tokens = ("--input-tokens", "10", "--output-tokens", "10")

    # No flag: old files keep working and the age is reported.
    result = _run(prices, *tokens)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["metadata"]["prices_age_days"] == 30

    # Within the window, including the boundary: still estimates.
    for limit in ("30", "90"):
        result = _run(prices, *tokens, "--max-age-days", limit)
        assert result.returncode == 0, (limit, result.stderr)

    # Past the window: fail closed with an actionable message.
    result = _run(prices, *tokens, "--max-age-days", "7")
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert not result.stdout
    assert "30 days ago" in result.stderr
    assert "--max-age-days 7" in result.stderr
    assert "re-read the provider pricing pages" in result.stderr

    result = _run(prices, *tokens, "--max-age-days", "-1")
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert "--max-age-days must be >= 0" in result.stderr
