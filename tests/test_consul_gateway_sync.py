import unittest

from scripts.consul_gateway_sync import ensure_safe_to_sync


class ConsulGatewaySyncSafetyTests(unittest.TestCase):

    def test_stops_when_no_workers_are_healthy(self):

        managed = {"http://worker-a:18000"}

        desired = set()

        with self.assertRaisesRegex(SystemExit, "Safety stop"):

            ensure_safe_to_sync(managed, desired)

    def test_allows_healthy_workers(self):

        managed = {

            "http://worker-a:18000",

            "http://worker-b:18001",

        }

        desired = set(managed)

        ensure_safe_to_sync(managed, desired)


if __name__ == "__main__":

    unittest.main()
