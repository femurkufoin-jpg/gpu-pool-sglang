import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from benchmarks.benchmark_gateway import send_request


class BenchmarkGatewayTests(unittest.IsolatedAsyncioTestCase):
    async def test_successful_response_records_latency(self):
        response = MagicMock()
        response.status = 200
        response.text = AsyncMock(return_value='{"choices": []}')

        request_context = MagicMock()
        request_context.__aenter__ = AsyncMock(return_value=response)
        request_context.__aexit__ = AsyncMock(return_value=False)

        session = MagicMock()
        session.post.return_value = request_context

        result = await send_request(
            session, "http://localhost:30000", "test-model",
            "Hello", asyncio.Semaphore(1)
        )

        self.assertTrue(result["ok"])
        self.assertGreaterEqual(result["latency_seconds"], 0)


    def test_median_summary_uses_middle_values(self):
       from benchmarks.benchmark_gateway import summarize_repetitions
       runs = [
           {
               "requests_per_second": 10.0,
               "latency_mean_seconds": 0.2,
               "latency_p50_seconds": 0.1,
               "latency_p95_seconds": 0.4,
               "requests_succeeded": 8,
               "requests_failed": 0,
           },
           {
               "requests_per_second": 20.0,
               "latency_mean_seconds": 0.4,
               "latency_p50_seconds": 0.2,
               "latency_p95_seconds": 0.6,
               "requests_succeeded": 7,
               "requests_failed": 1,
           },
           {
               "requests_per_second": 30.0,
               "latency_mean_seconds": 0.6,
               "latency_p50_seconds": 0.3,
               "latency_p95_seconds": 0.8,
               "requests_succeeded": 6,
               "requests_failed": 2,
           },
       ]
       summary = summarize_repetitions(8, runs)
       self.assertEqual(summary["repetitions"], 3)
       self.assertEqual(summary["median_requests_per_second"], 20.0)
       self.assertEqual(summary["median_latency_mean_seconds"], 0.4)
       self.assertEqual(summary["total_requests_succeeded"], 21)
       self.assertEqual(summary["total_requests_failed"], 3)

if __name__ == "__main__":
    unittest.main()
