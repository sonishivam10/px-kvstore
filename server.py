from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import json
from kv_store import KeyValueStore
import logging

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(threadName)s: %(message)s",
)
logger = logging.getLogger(__name__)

store = KeyValueStore()

class SimpleKVHandler(BaseHTTPRequestHandler):
    """HTTP request handler for key-value operations."""
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def _send_json(self, code, message):
        self._set_headers(code)
        response = json.dumps(message).encode("utf-8")
        self.wfile.write(response)

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            logger.info("Health check ping")
            return self._send_json(200, {"status": "ok"})

        elif parsed.path == "/keys":
            logger.info("Listing all valid keys")
            keys = store.list_keys()
            return self._send_json(200, {"keys": keys})
        
        elif parsed.path == "/store":
            params = parse_qs(parsed.query)
            key = params.get("key", [None])[0]
            if not key:
                logger.warning("GET missing key")
                return self._send_json(400, {"error": "Missing 'key'"})

            success, result = store.read(key)
            if success:
                logger.info("GET key='%s':%s", key, result)
                self._send_json(200, {"key": key, "value": result})
            else:
                logger.info("GET key='%s' not found", key)
                self._send_json(404, {"error": result})
        elif parsed.path == "/metrics":
            logger.info("Returning /metrics")
            return self._send_json(200, store.metrics())
        else:
            logger.warning("GET invalid path: %s", self.path)
            return self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        """Handle POST requests."""
        if self.path != "/store":
            logger.warning("POST invalid path: %s", self.path)
            return self._send_json(404, {"error": "Not found"})
        
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            key = data["key"]
            value = data["value"]
            ttl = data.get("ttl")
        except (KeyError, json.JSONDecodeError):
            logger.warning("POST invalid JSON: %s", body)
            return self._send_json(400, {"error": "Invalid JSON or missing fields"})

        success, result = store.create(key, value, ttl=int(ttl) if ttl else None)
        if success:
            logger.info("POST created key='%s' with ttl=%s", key, ttl)
            self._send_json(201, {"message": result})
        else:
            logger.info("POST failed: key='%s' already exists", key)
            self._send_json(400, {"message": result})

    def do_PUT(self):
        """Handle PUT requests."""
        if self.path != "/store":
            logger.warning("PUT invalid path: %s", self.path)
            return self._send_json(404, {"error": "Not found"})
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            key = data["key"]
            value = data["value"]
        except (KeyError, json.JSONDecodeError):
            logger.warning("PUT invalid JSON: %s", body)
            return self._send_json(400, {"error": "Invalid JSON or missing fields"})

        success, result = store.update(key, value)
        if success:
            logger.info("PUT updated key='%s' to value='%s'", key, value)
            self._send_json(200, {"message": result})
        else:
            logger.info("PUT failed key='%s' not found", key)
            self._send_json(404, {"message": result})

    def do_DELETE(self):
        """Handle DELETE requests."""
        parsed = urlparse(self.path)
        if parsed.path != "/store":
            logger.warning("DELETE invalid path: %s", self.path)
            return self._send_json(404, {"error": "Not found"})
        params = parse_qs(parsed.query)
        key = params.get("key", [None])[0]
        if not key:
            logger.warning("DELETE missing key param")
            return self._send_json(400, {"error": "Missing 'key'"})

        success, result = store.delete(key)
        if success:
            logger.info("DELETE removed key='%s'", key)
            self._send_json(200, {"message": result})
        else:
            logger.info("DELETE failed: key='%s' not found", key)
            self._send_json(404, {"message": result})

    
def run(server_class=ThreadingHTTPServer, handler_class=SimpleKVHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting thread-safe server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()