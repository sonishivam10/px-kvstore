import threading
import time
class KeyValueStore:
    def __init__(self):
        self.store = {}
        self.ttl_store = {}  # key : expiry timestamp
        self.lock = threading.Lock()

    def _is_expired(self, key):
        expiry = self.ttl_store.get(key)
        if expiry is None:
            return False
        if time.time() > expiry:
            # expired — clean up
            del self.store[key]
            del self.ttl_store[key]
            return True
        return False
        
    def create(self, key, value, ttl=None):
        with self.lock:
            if key in self.store:
                if not self._is_expired(key):
                    return False, "Key already exists."

            self.store[key] = value
            if ttl:
                self.ttl_store[key] = time.time() + ttl
            elif key in self.ttl_store:
                del self.ttl_store[key]
            return True, "Created."
    
    def read(self, key):
        with self.lock:
            if key not in self.store or self._is_expired(key):
                return False, "Key not found."
            return True, self.store[key]
    
    def update(self, key, value):
        with self.lock:
            if key not in self.store or self._is_expired(key):
                return False, "Key not found."
            self.store[key] = value
            return True, "Updated."
    
    def delete(self, key):
        with self.lock:
            if key not in self.store or self._is_expired(key):
                return False, "Key not found."
            del self.store[key]
            self.ttl_store.pop(key, None)
            return True, "Deleted."