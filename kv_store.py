class KeyValueStore:
    def __init__(self):
        self.store = {}
        
    def create(self, key, value):
        if key in self.store:
            return False, "Key already exists."
        
        self.store[key] = value
        return True, "Created."
    
    def read(self, key):
        if key not in self.store:
            return False, "Key not found."
        
        return True, self.store[key]
    
    def update(self, key, value):
        if key not in self.store:
            return False, "Key not found."
        self.store[key] = value
        return True, "Updated."
    
    def delete(self, key):
        if key not in self.store:
            return False, "Key not found."
        del self.store[key]
        return True, "Deleted."