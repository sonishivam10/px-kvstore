import threading
import time
class KeyValueStore:
    """Thread-safe in-memory key-value store with TTL support."""

    def __init__(self):
        self.store = {}
        self.ttl_store = {}  # key : expiry timestamp
        self.lock = threading.Lock()
        self.start_time = time.time()

    def _is_expired(self, key):
        """Check if a key has expired."""
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
        """Create a key-value pair with optional TTL in seconds."""
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
        """Read value by key, return False if not found or expired."""
        with self.lock:
            if key not in self.store or self._is_expired(key):
                return False, "Key not found."
            return True, self.store[key]
    
    def update(self, key, value):
        """Update new value by key, return False if not found or expired."""
        with self.lock:
            if key not in self.store or self._is_expired(key):
                return False, "Key not found."
            self.store[key] = value
            return True, "Updated."
    
    def delete(self, key):
        """Delete a key, return True if key existed."""
        with self.lock:
            if key not in self.store or self._is_expired(key):
                return False, "Key not found."
            del self.store[key]
            self.ttl_store.pop(key, None)
            return True, "Deleted."
    
    def list_keys(self):
        """Get all non-expired keys."""
        with self.lock:
            keys = list(self.store.keys())
            valid_keys = [key for key in keys if not self._is_expired(key)]
            return valid_keys
    
    def metrics(self):
        """Get metrics of KeyValue Store"""
        with self.lock:
            now = time.time()
            total_keys = len(self.store)
            valid_keys = len([k for k in self.store if not self._is_expired(k)])
            ttl_keys = len(self.ttl_store)
            return {
                "uptime_seconds": int(now - self.start_time),
                "total_keys": total_keys,
                "valid_keys": valid_keys,
                "ttl_keys": ttl_keys
            }