#!/usr/bin/env python3
"""Tests for training_math.py.

Each test pins a function to a value published in a paper or derivable by hand, so
a wrong formula (a dropped term, a swapped exponent, the wrong N convention) fails
here instead of shipping as a worked example. Run: python3 scripts/test_training_math.py
"""

import importlib.util
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "training_math.py"

_spec = importlib.util.spec_from_file_location("ai_scaling_laws_training_math", SCRIPT)
tm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tm)

GPT2 = dict(n_layer=12, d_model=768, vocab=50257, context=1024)


class DecoderParams(unittest.TestCase):
    def test_gpt2_124m_matches_published_count(self):
        # GPT-2 small: 124,439,808 parameters with the LM head tied to wte.
        p = tm.decoder_params(**GPT2)
        self.assertEqual(p["total"], 124_439_808)
        self.assertEqual(p["per_layer"], 7_087_872)  # 12d^2 + 13d
        self.assertEqual(p["per_layer"], 12 * 768**2 + 13 * 768)
        self.assertEqual(p["non_embedding"], 85_056_000)

    def test_untied_head_adds_one_vocab_matrix_not_double(self):
        tied = tm.decoder_params(**GPT2)["total"]
        untied = tm.decoder_params(**GPT2, tied=False)["total"]
        self.assertEqual(untied - tied, 50257 * 768)
        self.assertAlmostEqual(untied / tied, 1.31, places=2)

    def test_llama2_7b_gated_rmsnorm_untied(self):
        # Llama 2 7B: d=4096, L=32, V=32000, SwiGLU width 11008, RMSNorm, no bias,
        # untied head, RoPE: 6,738,415,616 parameters.
        p = tm.decoder_params(32, 4096, 32000, context=0, ffn_hidden=11008,
                              gated_ffn=True, rmsnorm=True, bias=False, tied=False)
        self.assertEqual(p["total"], 6_738_415_616)

    def test_gqa_shrinks_only_k_and_v(self):
        mha = tm.decoder_params(1, 64, 10, n_head=8, n_kv_head=8, bias=False)
        gqa = tm.decoder_params(1, 64, 10, n_head=8, n_kv_head=2, bias=False)
        # K and V go from 64x64 each to 64x16 each.
        self.assertEqual(mha["per_layer"] - gqa["per_layer"], 2 * 64 * (64 - 16))

    def test_rejects_bad_shapes(self):
        with self.assertRaises(ValueError):
            tm.decoder_params(0, 768, 50257)
        with self.assertRaises(ValueError):
            tm.decoder_params(12, 768, 50257, n_head=7, n_kv_head=7)
        with self.assertRaises(ValueError):
            tm.decoder_params(12, 768, 50257, n_head=12)


class Flops(unittest.TestCase):
    def test_6nd_chinchilla(self):
        # Chinchilla: 70B params x 1.4T tokens = 5.88e23 FLOPs.
        self.assertAlmostEqual(tm.training_flops_6nd(70e9, 1.4e12) / 5.88e23, 1.0, places=6)

    def test_palm_form_adds_attention_term(self):
        n = tm.decoder_params(**GPT2)["matmul"]
        fpt = tm.palm_flops_per_token(n, 12, 768, 1024)
        self.assertEqual(fpt, 6 * n + 12 * 12 * 768 * 1024)
        # Against the Kaplan-style 6 * N_nonemb, the PaLM form is 1.68x at 124M.
        self.assertAlmostEqual(fpt / (6 * 85_056_000), 1.676, places=3)

    def test_mfu_reproduces_palm_table_3(self):
        # PaLM App. B: MT-NLG 530B, 65.43K tok/s on 2240 A100s at 312 TFLOP/s -> 29.7%
        # without attention; PaLM 540B, 238.3K tok/s on 6144 TPUv4 at 275 TFLOP/s -> 45.7%.
        self.assertAlmostEqual(tm.mfu(65.43e3, 6 * 530e9, 2240, 312e12), 0.297, delta=0.001)
        self.assertAlmostEqual(tm.mfu(238.3e3, 6 * 540e9, 6144, 275e12), 0.457, delta=0.001)

    def test_hours_is_inverse_of_mfu(self):
        h = tm.train_hours(6e20, 8, 312e12, 0.40)
        self.assertAlmostEqual(h, 166.93, places=1)
        tokens_per_sec = 100e9 / (h * 3600)
        self.assertAlmostEqual(tm.mfu(tokens_per_sec, 6 * 1e9, 8, 312e12), 0.40, places=9)

    def test_hours_rejects_impossible_utilization(self):
        with self.assertRaises(ValueError):
            tm.train_hours(1e20, 8, 312e12, 1.5)

    def test_mfu_rejects_impossible_utilization(self):
        with self.assertRaisesRegex(ValueError, "mfu.*greater than 1"):
            tm.mfu(2e6, 6e12, 1, 1e18)
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "mfu", "--tokens-per-sec", "2e6",
             "--flops-per-token", "6e12", "--gpus", "1", "--peak", "1e18"],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(r.returncode, 2)
        self.assertIn("mfu", r.stderr)
        self.assertFalse(r.stdout)


class ComputeOptimal(unittest.TestCase):
    def test_20to1_is_6nd_algebra(self):
        n, d = tm.chinchilla_20to1(1.2e20)
        self.assertAlmostEqual(n, 1e9, delta=1)
        self.assertAlmostEqual(d, 20e9, delta=20)

    def test_published_vs_refit_fit_direction(self):
        # Hoffmann's eq.-3 constants imply far more than 20 tok/param at Chinchilla's
        # budget; the Besiroglu refit restores roughly 20 (arXiv 2404.10102).
        n, d = tm.parametric_optimum(5.76e23, 406.4, 410.7, 0.34, 0.28)
        self.assertAlmostEqual(d / n, 92.6, delta=0.5)
        n, d = tm.parametric_optimum(5.76e23, 482.01, 2085.43, 0.3478, 0.3658)
        self.assertAlmostEqual(d / n, 18.4, delta=0.5)

    def test_parametric_optimum_is_a_minimum(self):
        consts = (482.01, 2085.43, 0.3478, 0.3658)
        c = 1e22
        n, d = tm.parametric_optimum(c, *consts)
        self.assertAlmostEqual(6 * n * d / c, 1.0, places=9)
        loss = lambda nn: consts[0] / nn ** consts[2] + consts[1] / (c / 6 / nn) ** consts[3]
        self.assertLess(loss(n), loss(n * 1.1))
        self.assertLess(loss(n), loss(n / 1.1))


class Lsh(unittest.TestCase):
    def test_s_curve_formula(self):
        self.assertAlmostEqual(tm.lsh_candidate_probability(0.5, 2, 1), 0.75)  # 1-(1-.5)^2
        self.assertAlmostEqual(tm.lsh_candidate_probability(0.5, 1, 3), 0.125)  # s^r
        self.assertAlmostEqual(tm.lsh_candidate_probability(0.8, 20, 6), 0.9977, places=4)
        self.assertEqual(tm.lsh_candidate_probability(0.0, 14, 8), 0.0)
        self.assertEqual(tm.lsh_candidate_probability(1.0, 14, 8), 1.0)

    def test_threshold_and_monotonic(self):
        self.assertAlmostEqual(tm.lsh_threshold(14, 8), (1 / 14) ** (1 / 8))
        ps = [tm.lsh_candidate_probability(s / 20, 14, 8) for s in range(21)]
        self.assertEqual(ps, sorted(ps))
        # More bands, same rows: lower threshold, higher P at a fixed similarity.
        self.assertGreater(tm.lsh_candidate_probability(0.7, 20, 8),
                           tm.lsh_candidate_probability(0.7, 14, 8))

    def test_rejects_similarity_outside_unit_interval(self):
        with self.assertRaises(ValueError):
            tm.lsh_candidate_probability(1.2, 14, 8)


class Activations(unittest.TestCase):
    def test_korthikanti_table(self):
        # Korthikanti et al. 2022: 5as/h = 80 for GPT-3 (a=96, s=2048, h=12288).
        r = tm.activation_memory_bytes(2048, 1, 12288, 1, 96)
        self.assertAlmostEqual(r["per_layer"], 2048 * 12288 * (34 + 80))
        # Tensor parallel t=8: sbh(10 + 24/t + 5as/(ht)).
        r = tm.activation_memory_bytes(2048, 1, 12288, 1, 96, tp=8)
        self.assertAlmostEqual(r["per_layer"], 2048 * 12288 * (10 + 3 + 10))
        r = tm.activation_memory_bytes(2048, 1, 12288, 1, 96, tp=8, sequence_parallel=True)
        self.assertAlmostEqual(r["per_layer"], 2048 * 12288 * (34 / 8 + 10))

    def test_flash_drops_quadratic_term(self):
        full = tm.activation_memory_bytes(8192, 1, 4096, 32, 32)
        flash = tm.activation_memory_bytes(8192, 1, 4096, 32, 32, flash_attention=True)
        self.assertAlmostEqual(full["total"] / 1e9, 380.1, places=1)
        self.assertAlmostEqual(flash["total"] / 1e9, 36.5, places=1)
        self.assertAlmostEqual(full["quadratic_share"], 0.904, places=3)
        self.assertEqual(flash["quadratic_share"], 0.0)


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args],
                              capture_output=True, text=True, timeout=60)

    def test_help(self):
        r = self.run_cli("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("activations", r.stdout)

    def test_json_output(self):
        r = self.run_cli("--json", "params", "--layers", "12", "--d-model", "768",
                         "--vocab", "50257", "--context", "1024")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["total"], 124_439_808)

    def test_bad_input_fails_closed(self):
        for args in (["bogus"], ["lsh", "--bands", "0", "--rows", "8"],
                     ["hours", "--flops", "1e20", "--gpus", "8", "--peak", "3e14", "--mfu", "2"],
                     ["flops", "--params", "1e9", "--tokens", "1e10", "--layers", "12"],
                     ["--json", "flops", "--params", "1e308", "--tokens", "1e308"],
                     ["mfu", "--tokens-per-sec", "nan", "--flops-per-token", "1", "--gpus", "1",
                      "--peak", "1"]):
            r = self.run_cli(*args)
            self.assertEqual(r.returncode, 2, args)
            self.assertIn("error", r.stderr)


if __name__ == "__main__":
    unittest.main()
