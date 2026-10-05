import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import latency_benchmark


class LatencyBenchmarkTests(unittest.TestCase):
    def test_partial_request_failure_returns_nonzero_and_reports_failures(self):
        def request(index, *_args):
            status = 200 if index == 0 else 503
            return latency_benchmark.RequestResult(index, 0.01, status, 1 if status == 200 else 0, "")

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "report.json"
            with patch.object(latency_benchmark, "_do_request", side_effect=request):
                with contextlib.redirect_stdout(io.StringIO()):
                    result = latency_benchmark.run("http://localhost:8000/v1", "local-model", "hi", 2, 1, None, 8, 1.0, output)

            self.assertEqual(result, 1)
            self.assertIn('"failed": 1', output.read_text())

    def test_malformed_success_body_is_a_failed_request(self):
        class Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return b"not json"

        with patch.object(latency_benchmark.urllib.request, "urlopen", return_value=Response()):
            result = latency_benchmark._do_request(0, "http://localhost:8000/v1/chat/completions", {}, b"{}", 1.0)

        self.assertNotEqual(result.status, 200)


if __name__ == "__main__":
    unittest.main()
