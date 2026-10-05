"""CLI regression tests for baseline completeness, sample-size gating and calibration."""

import json
import re
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("ts_evaluator.py")


def _run(tmp_path, rows, command="backtest", extra=None, args=()):
    source = tmp_path / "forecast.json"
    source.write_text(json.dumps({"backtest_windows": rows, **(extra or {})}), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), command, "--input", str(source), *args],
        capture_output=True, text=True, check=False,
    )


def _origins(n, **row):
    return [{"origin_date": f"2026-01-{i + 1:02d}", **row} for i in range(n)]


def test_partial_seasonal_baseline_fails_closed(tmp_path):
    rows = [
        {"origin_date": "2026-01-01", "horizon_h": 7,
         "actual_value": 10, "point_forecast": 11, "origin_value": 0,
         "seasonal_naive_forecast": 10},
        {"origin_date": "2026-01-02", "horizon_h": 7,
         "actual_value": 10, "point_forecast": 11, "origin_value": 0},
    ]
    result = _run(tmp_path, rows)
    assert result.returncode == 2, result.stdout
    assert not result.stdout
    assert "seasonal_naive_forecast" in result.stderr
    assert "horizon 7" in result.stderr


def test_no_seasonal_baseline_remains_valid(tmp_path):
    rows = [{"origin_date": "2026-01-01", "horizon_h": 7,
             "actual_value": 10, "point_forecast": 9, "origin_value": 0}]
    result = _run(tmp_path, rows)
    assert result.returncode == 0, result.stderr
    assert "naive" in result.stdout


def test_zero_error_seasonal_baseline_marks_worse_model_as_worse(tmp_path):
    # The seasonal naive is exact, so any model error is worse than it; the warning must
    # name that baseline and its field, not call skill "undefined" or blame origin_value.
    rows = _origins(6, horizon_h=7, actual_value=10, point_forecast=11, origin_value=0,
                    seasonal_naive_forecast=10)
    for command in ("backtest", "report"):
        result = _run(tmp_path, rows, command)
        assert result.returncode == 0, result.stderr
        assert "worse than baseline" in result.stdout
        assert "seasonal naive baseline has zero error" in result.stdout
        assert "seasonal_naive_forecast" in result.stdout
        assert "undefined" not in result.stdout
        assert "check origin_value" not in result.stdout


def test_seasonal_baseline_missing_for_a_horizon_fails_closed(tmp_path):
    rows = [
        {"origin_date": "2026-01-01", "horizon_h": 1,
         "actual_value": 10, "point_forecast": 11, "origin_value": 0,
         "seasonal_naive_forecast": 10},
        {"origin_date": "2026-01-01", "horizon_h": 2,
         "actual_value": 10, "point_forecast": 11, "origin_value": 0},
    ]
    result = _run(tmp_path, rows)
    assert result.returncode == 2, result.stdout
    assert not result.stdout
    assert "seasonal_naive_forecast" in result.stderr
    assert "horizons [2]" in result.stderr


def test_calibration_ignores_partial_seasonal_baselines(tmp_path):
    # Calibration scores interval coverage only and never reads seasonal_naive_forecast,
    # so a baseline supplied for some horizons must not block it; backtest and report
    # compare against that baseline and must still fail closed on the same file.
    interval = {"lower_50": 9, "upper_50": 11, "lower_80": 8, "upper_80": 12,
                "lower_90": 7, "upper_90": 13}
    rows = [
        {"origin_date": "2026-01-01", "horizon_h": 1, "actual_value": 10,
         "point_forecast": 11, "origin_value": 0, "seasonal_naive_forecast": 10, **interval},
        {"origin_date": "2026-01-01", "horizon_h": 2, "actual_value": 10,
         "point_forecast": 11, "origin_value": 0, **interval},
    ]
    result = _run(tmp_path, rows, "calibration")
    assert result.returncode == 0, result.stderr
    assert "CALIBRATION ANALYSIS" in result.stdout
    for command in ("backtest", "report"):
        result = _run(tmp_path, rows, command)
        assert result.returncode == 2, (command, result.stdout)
        assert not result.stdout
        assert "every horizon or none" in result.stderr


def test_calibration_still_rejects_non_numeric_seasonal_baseline(tmp_path):
    rows = [{"origin_date": "2026-01-01", "horizon_h": 1, "actual_value": 10,
             "point_forecast": 11, "origin_value": 0, "seasonal_naive_forecast": "x",
             "lower_50": 9, "upper_50": 11}]
    result = _run(tmp_path, rows, "calibration")
    assert result.returncode == 2, result.stdout
    assert "seasonal_naive_forecast must be a finite number" in result.stderr


def test_unloadable_input_file_exits_2_naming_the_file(tmp_path):
    not_utf8 = tmp_path / "latin1.json"
    not_utf8.write_bytes(b'{"model_name":"caf\xe9"}')
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{not json", encoding="utf-8")
    huge_int = tmp_path / "huge.json"
    huge_int.write_text('{"n":' + "1" * 5000 + "}", encoding="utf-8")
    missing = tmp_path / "missing.json"
    for path in (not_utf8, bad_json, huge_int, missing, tmp_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "backtest", "--input", str(path)],
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == 2, (path, result.stdout, result.stderr)
        assert not result.stdout
        assert "Traceback" not in result.stderr
        assert str(path) in result.stderr


def test_pooled_coverage_cannot_hide_a_failing_horizon(tmp_path):
    # h=1 covers 20/20 and h=30 covers 12/20 at 80%: the pool is exactly 80%, but h=30 is
    # over-confident and must decide the level's verdict.
    inside = {"lower_80": 9, "upper_80": 11}
    rows = _origins(20, horizon_h=1, actual_value=10, point_forecast=10, origin_value=10, **inside)
    rows += [{**r, "horizon_h": 30, "actual_value": 10 if i < 12 else 20}
             for i, r in enumerate(_origins(20, point_forecast=10, origin_value=10, **inside))]
    for command in ("calibration", "report"):
        result = _run(tmp_path, rows, command)
        assert result.returncode == 0, result.stderr
        h30 = [line for line in result.stdout.splitlines() if "80%" in line and "h=30" in line]
        assert h30 and all("over-confident" in line for line in h30), result.stdout
        verdict = [line for line in result.stdout.splitlines() if line.strip(" -").startswith("80%:")]
        assert verdict and "over-confident at h=30" in verdict[0], result.stdout
        assert "good" not in result.stdout


def test_calibrated_n50_sample_is_not_flagged(tmp_path):
    # 29/50, 37/50 and 42/50 inside the 50/80/90% intervals: 6-8 pp from nominal, which is
    # binomial noise at n=50, so no level may be called over- or under-confident.
    def row(d):
        return {"horizon_h": 1, "actual_value": d, "point_forecast": 0, "origin_value": 0,
                "lower_50": -1, "upper_50": 1, "lower_80": -2, "upper_80": 2,
                "lower_90": -3, "upper_90": 3}
    offsets = [0.5] * 29 + [1.5] * 8 + [2.5] * 5 + [3.5] * 8
    rows = [{"origin_date": f"origin-{i}", **row(d)} for i, d in enumerate(offsets)]
    result = _run(tmp_path, rows, "calibration")
    assert result.returncode == 0, result.stderr
    assert "over-confident" not in result.stdout
    assert "under-confident" not in result.stdout
    assert result.stdout.count("consistent with nominal at every horizon (independence assumed;") == 3


def test_single_origin_cannot_earn_beats_baseline(tmp_path):
    one = _origins(1, horizon_h=1, actual_value=10, point_forecast=10, origin_value=0)
    for command in ("backtest", "report"):
        result = _run(tmp_path, one, command)
        assert result.returncode == 0, result.stderr
        assert "beats baseline" not in result.stdout.replace('"beats baseline"', "")
        assert "insufficient origins" in result.stdout
    # The gate lifts once there are enough distinct origins.
    six = _origins(6, horizon_h=1, actual_value=10, point_forecast=10, origin_value=0)
    result = _run(tmp_path, six)
    assert "beats baseline  (6 origins)" in result.stdout


def test_huge_finite_values_exit_2_with_a_rescale_hint(tmp_path):
    rows = [{"origin_date": "2026-01-01", "horizon_h": 1, "actual_value": 1e200,
             "point_forecast": 0, "origin_value": 0}]
    for command in ("backtest", "report"):
        result = _run(tmp_path, rows, command)
        assert result.returncode == 2, (command, result.stdout, result.stderr)
        assert not result.stdout
        assert "Traceback" not in result.stderr
        assert "actual_value" in result.stderr and "rescale" in result.stderr
    huge_int = tmp_path / "huge_int.json"
    huge_int.write_text('{"backtest_windows": [{"origin_date": "d", "horizon_h": 1, '
                        '"actual_value": 1' + "0" * 400 + ', "point_forecast": 0, '
                        '"origin_value": 0}]}', encoding="utf-8")
    result = subprocess.run([sys.executable, str(SCRIPT), "backtest", "--input", str(huge_int)],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 2 and "Traceback" not in result.stderr, result.stderr


def test_report_output_to_a_directory_exits_2(tmp_path):
    rows = [{"origin_date": "2026-01-01", "horizon_h": 1, "actual_value": 10,
             "point_forecast": 9, "origin_value": 8}]
    result = _run(tmp_path, rows, "report", args=("--output", str(tmp_path)))
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert "Traceback" not in result.stderr
    assert "--output needs a file path" in result.stderr


def test_report_header_lists_horizons_from_the_data(tmp_path):
    rows = [{"origin_date": "2026-01-01", "horizon_h": 1, "actual_value": 10,
             "point_forecast": 9, "origin_value": 8}]
    result = _run(tmp_path, rows, "report", extra={"forecast_horizons": [99, "x"]})
    assert result.returncode == 0, result.stderr
    assert "**Forecast horizons:** [1]" in result.stdout


def test_repeating_origins_across_horizons_cannot_create_calibration_evidence(tmp_path):
    # Repeat exactly the same 8/12 hits at four horizons. Pooling them as 48 independent
    # trials falsely increases power; the pooled row must have no CI or inferential verdict.
    rows = []
    for h in (1, 7, 14, 30):
        rows += [{**r, "horizon_h": h, "actual_value": 10 if i < 8 else 20}
                 for i, r in enumerate(_origins(12, point_forecast=10, origin_value=10,
                                                lower_80=9, upper_80=11))]
    for command in ("calibration", "report"):
        result = _run(tmp_path, rows, command)
        assert result.returncode == 0, result.stderr
        verdict = [line for line in result.stdout.splitlines() if line.strip(" -").startswith("80%:")]
        assert verdict and "consistent with nominal at every horizon" in verdict[0], result.stdout
        assert "over-confident pooled" not in result.stdout
        assert "descriptive only (shared origins)" in result.stdout
        assert "independent coverage hits" in result.stdout
        pooled = [line for line in result.stdout.splitlines() if "pooled (12 origins)" in line]
        assert pooled and "N/A" in pooled[0], result.stdout


def test_partial_interval_level_fails_closed_without_report_output(tmp_path):
    rows = _origins(6, horizon_h=7, actual_value=10, point_forecast=10, origin_value=0,
                    lower_80=9, upper_80=11)
    rows[-1].pop("lower_80")
    rows[-1].pop("upper_80")
    output = tmp_path / "report.md"
    output.write_text("existing report", encoding="utf-8")
    for command in ("calibration", "report"):
        args = ("--output", str(output)) if command == "report" else ()
        result = _run(tmp_path, rows, command, args=args)
        assert result.returncode == 2, (command, result.stdout, result.stderr)
        assert not result.stdout
        assert "backtest_windows[5]: 80% interval must be supplied for every row or none" in result.stderr
        assert output.read_text(encoding="utf-8") == "existing report"


def test_interval_level_missing_for_an_entire_horizon_fails_closed(tmp_path):
    rows = _origins(6, horizon_h=1, actual_value=10, point_forecast=10, origin_value=0,
                    lower_80=9, upper_80=11)
    rows += _origins(6, horizon_h=7, actual_value=20, point_forecast=10, origin_value=0)
    for command in ("calibration", "report"):
        result = _run(tmp_path, rows, command)
        assert result.returncode == 2, (command, result.stdout, result.stderr)
        assert not result.stdout
        assert "backtest_windows[6]: 80% interval must be supplied for every row or none" in result.stderr


def test_mape_skips_near_zero_actuals_and_prints_no_inf(tmp_path):
    rows = _origins(6, horizon_h=1, actual_value=1e-300, point_forecast=1e150, origin_value=1e-300)
    for command in ("backtest", "report"):
        result = _run(tmp_path, rows, command)
        assert result.returncode == 0, result.stderr
        assert not re.search(r"\b-?(inf|nan)\b", result.stdout), result.stdout
        assert "excludes 6 of 6 row(s) whose actual is ~0" in result.stdout


def test_metric_overflow_from_a_near_zero_denominator_exits_2(tmp_path):
    rows = [{"origin_date": "2026-01-01", "horizon_h": 1, "actual_value": 5,
             "point_forecast": 4, "origin_value": 3}]
    result = _run(tmp_path, rows, extra={"history_values": [0, 5e-324, 0, 5e-324]})
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert not result.stdout
    assert "Traceback" not in result.stderr
    assert "computed mase is not a finite number" in result.stderr
