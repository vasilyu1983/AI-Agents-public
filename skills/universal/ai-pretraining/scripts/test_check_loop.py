#!/usr/bin/env python3
"""Tests for check_loop.py: it must fail on a broken user model, not only pass on its own demo.

The 2026-09 audit found the script only checked a model it defined itself, so it
could never fail on the user's bug, and it accepted any flag. Each buggy model
below carries one defect the matching check must catch. Needs PyTorch; skipped
(with the reason printed) when torch is absent.
"""

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "check_loop.py"

try:
    import torch  # noqa: F401
    HAVE_TORCH = True
except ImportError:
    HAVE_TORCH = False

MODELS = textwrap.dedent('''
    import torch, torch.nn as nn, torch.nn.functional as F

    class LM(nn.Module):
        def __init__(self, causal=True, emb_std=0.02, batch_mix=False, V=300, d=32):
            super().__init__()
            self.causal, self.batch_mix = causal, batch_mix
            self.emb = nn.Embedding(V, d)
            nn.init.normal_(self.emb.weight, std=emb_std)
            self.qkv = nn.Linear(d, 3 * d)
            self.head = nn.Linear(d, V, bias=False)
            self.head.weight = self.emb.weight

        def forward(self, idx, targets=None):
            x = self.emb(idx)
            if self.batch_mix:  # statistics across the batch: micro-batches no longer add up
                x = x - x.mean(dim=0, keepdim=True)
            q, k, v = self.qkv(x).chunk(3, dim=-1)
            y = F.scaled_dot_product_attention(q, k, v, is_causal=self.causal)
            return self.head(x + y), None

    def good():
        torch.manual_seed(0); return LM()
    def no_mask():
        torch.manual_seed(0); return LM(causal=False)
    def bad_init():
        torch.manual_seed(0); return LM(emb_std=1.0)
    def batch_mix():
        torch.manual_seed(0); return LM(batch_mix=True)
''')


def run(*args, cwd=None):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=cwd)


class UsageTests(unittest.TestCase):
    def test_unknown_flag_exits_2(self):
        self.assertEqual(run("--bogus", "notafile").returncode, 2)

    def test_empty_model_does_not_run_demo(self):
        r = run("--model", "")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertNotIn("DEMO", r.stdout)

    def test_nonfinite_tolerance_exits_2(self):
        self.assertEqual(run("--tol", "inf").returncode, 2)


@unittest.skipUnless(HAVE_TORCH, "PyTorch not installed: model checks not run")
class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.models = Path(cls.tmp.name) / "models.py"
        cls.models.write_text(MODELS)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def check(self, factory):
        return run("--model", f"{self.models}:{factory}")

    def test_demo_passes_and_says_demo(self):
        r = run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("DEMO", r.stdout)

    def test_good_model_passes(self):
        r = self.check("good")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_missing_mask_fails_causality(self):
        r = self.check("no_mask")
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL  causality", r.stdout)

    def test_optimized_python_still_rejects_future_leak(self):
        r = subprocess.run(
            [sys.executable, "-O", str(SCRIPT), "--model", f"{self.models}:no_mask"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("FAIL  causality", r.stdout)

    def test_bad_init_fails_baseline_loss(self):
        r = self.check("bad_init")
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL  baseline loss", r.stdout)

    def test_batch_dependent_forward_fails_grad_accumulation(self):
        r = self.check("batch_mix")
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL  grad accumulation", r.stdout)

    def test_missing_factory_exits_2(self):
        self.assertEqual(self.check("nope").returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
