import unittest
from kv_store import KeyValueStore

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

if __name__ == '__main__':
    unittest.main()
