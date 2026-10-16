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


if __name__ == "__main__":
    unittest.main()
