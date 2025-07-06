import threading
class KeyValueStore:
    def __init__(self):
        self.store = {}
        self.lock = threading.Lock()
        
    def create(self, key, value):
        with self.lock:
            if key in self.store:
                return False, "Key already exists."
            
            self.store[key] = value
            return True, "Created."
    
    def read(self, key):
        with self.lock:
            if key not in self.store:
                return False, "Key not found."
            
            return True, self.store[key]
    
    def update(self, key, value):
        with self.lock:
            if key not in self.store:
                return False, "Key not found."
            self.store[key] = value
            return True, "Updated."
    
    def delete(self, key):
        with self.lock:
            if key not in self.store:
                return False, "Key not found."
            del self.store[key]
            return True, "Deleted."