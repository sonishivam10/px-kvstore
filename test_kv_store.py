import unittest
import threading
import logging
from kv_store import KeyValueStore

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


if __name__ == '__main__':
    unittest.main()
