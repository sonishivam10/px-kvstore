import http
import json
import time
import unittest
import threading
import logging
from kv_store import KeyValueStore
from server import run, store

# Setup logging for test environment
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(threadName)s: %(message)s"
)
logger = logging.getLogger(__name__)

class TestKeyValueStore(unittest.TestCase):
    def setUp(self):
        self.store = KeyValueStore()

    def test_create_key(self):
        success, msg = self.store.create("P", "PhysicsX")
        self.assertTrue(success)
        self.assertEqual(msg, "Created.")

    def test_create_existing_key(self):
        self.store.create("P", "PhysicsX")
        success, msg = self.store.create("P", "PhysicsWithoutX")
        self.assertFalse(success)
        self.assertEqual(msg, "Key already exists.")

    def test_read_key(self):
        self.store.create("F", "Formula-1")
        success, val = self.store.read("F")
        self.assertTrue(success)
        self.assertEqual(val, "Formula-1")

    def test_read_missing_key(self):
        success, msg = self.store.read("missing")
        self.assertFalse(success)
        self.assertEqual(msg, "Key not found.")

    def test_update_key(self):
        self.store.create("T", "Tesla")
        success, msg = self.store.update("T", "Triumph")
        self.assertTrue(success)
        self.assertEqual(msg, "Updated.")
        self.assertEqual(self.store.store["T"], "Triumph")

    def test_update_missing_key(self):
        success, msg = self.store.update("missing", "value")
        self.assertFalse(success)
        self.assertEqual(msg, "Key not found.")

    def test_delete_key(self):
        self.store.create("D", "Defense")
        success, msg = self.store.delete("D")
        self.assertTrue(success)
        self.assertEqual(msg, "Deleted.")
        self.assertNotIn("D", self.store.store)

    def test_delete_missing_key(self):
        success, msg = self.store.delete("Automation")
        self.assertFalse(success)
        self.assertEqual(msg, "Key not found.")

    def test_concurrent_access(self):
        def worker(thread_id):
            key = f"user-{thread_id}"
            logger.info("Thread starting operations on key='%s'", key)

            success, msg = self.store.create(key, f"init-{thread_id}")
            logger.info("CREATE: key='%s' => %s", key, msg)

            success, msg = self.store.update(key, f"updated-{thread_id}")
            logger.info("UPDATE: key='%s' => %s", key, msg)

            success, val = self.store.read(key)
            if success:
                logger.info("READ: key='%s' => %s", key, val)
            else:
                logger.warning("READ: key='%s' => %s", key, val)

            success, msg = self.store.delete(key)
            logger.info("DELETE: key='%s' => %s", key, msg)

            logger.info("Thread finished operations on key='%s'", key)

        threads = []
        for i in range(10):  # 10 concurrent threads
            t = threading.Thread(target=worker, args=(i,), name=f"Worker-{i}")
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(self.store.store), 0)

class TestKeyValueStoreTTL(unittest.TestCase):
    def setUp(self):
        self.store = KeyValueStore()

    def test_ttl_expiry(self):
        logger.info("Creating key 'temp' with TTL=1s")
        self.store.create("temp", "value", ttl=1)

        success, val = self.store.read("temp")
        logger.info("Read immediately: %s = %s", success, val)
        self.assertTrue(success)

        logger.info("Sleeping 1.5s to allow TTL expiry")
        time.sleep(1.5)

        success, msg = self.store.read("temp")
        logger.info("Read after expiry: %s = %s", success, msg)
        self.assertFalse(success)
        self.assertEqual(msg, "Key not found.")


    def test_ttl_update_before_expiry(self):
        logger.info("Creating key 'temp' with TTL=2s")
        self.store.create("temp", "value", ttl=2)

        logger.info("Sleeping 1s before update")
        time.sleep(1)

        success, msg = self.store.update("temp", "updated")
        logger.info("Update before expiry: %s = %s", success, msg)
        self.assertTrue(success)

        logger.info("Sleeping 1.5s to exceed TTL")
        time.sleep(1.5)

        success, msg = self.store.read("temp")
        logger.info("Read after TTL should have expired: %s = %s", success, msg)
        self.assertFalse(success)


    def test_ttl_prevents_delete(self):
        logger.info("Creating key 'temp' with TTL=1s")
        self.store.create("temp", "value", ttl=1)

        logger.info("Sleeping 1.2s to expire key")
        time.sleep(1.2)

        success, msg = self.store.delete("temp")
        logger.info("Delete after TTL expiry: %s = %s", success, msg)
        self.assertFalse(success)
        self.assertEqual(msg, "Key not found.")

class TestHTTPAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8081
        cls.server_thread = threading.Thread(target=run, kwargs={"port": cls.port}, daemon=True)
        cls.server_thread.start()
        time.sleep(1)  # Give the server time to start

    def request(self, method, path, body=None):
        conn = http.client.HTTPConnection("localhost", self.port)
        headers = {"Content-Type": "application/json"} if body else {}
        conn.request(method, path, body=json.dumps(body) if body else None, headers=headers)
        response = conn.getresponse()
        return response.status, json.loads(response.read())

    def test_health_check(self):
        logger.info("Testing /health endpoint")
        status, data = self.request("GET", "/health")
        logger.info("Status: %d, Response: %s", status, data)
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "ok")
        logger.info("/health endpoint passed\n")

    def test_keys_listing(self):
        logger.info("Testing /keys endpoint")
        logger.info("Creating keys: x, y (with TTL), z")
        store.create("x", "1")
        store.create("y", "2", ttl=1)
        store.create("z", "3")

        logger.info("Sleeping 1.2s to let TTL expire for 'y'")
        time.sleep(1.2)  # 'y' expire
        status, data = self.request("GET", "/keys")

        logger.info("Status: %d, Response: %s", status, data)
        self.assertEqual(status, 200)
        self.assertIn("keys", data)
        self.assertIn("x", data["keys"])
        self.assertIn("z", data["keys"])
        self.assertNotIn("y", data["keys"])
        logger.info("/keys endpoint passed\n")

    def test_metrics_endpoint(self):
        logger.info("Testing /metrics endpoint")
        status, data = self.request("GET", "/metrics")

        logger.info("Status: %d, Response: %s", status, data)
        self.assertEqual(status, 200)
        self.assertIn("uptime_seconds", data)
        self.assertIn("total_keys", data)
        self.assertIn("valid_keys", data)
        self.assertIn("ttl_keys", data)
        self.assertGreaterEqual(data["uptime_seconds"], 0)

        logger.info("/metrics endpoint passed\n")

if __name__ == '__main__':
    unittest.main()
