from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
from kv_store import KeyValueStore

store = KeyValueStore()

class SimpleKVHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def _send_json(self, code, message):
        self._set_headers(code)
        response = json.dumps(message).encode("utf-8")
        self.wfile.write(response)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/store":
            return self._send_json(404, {"error": "Not found"})
        
        params = parse_qs(parsed.query)
        key = params.get("key", [None])[0]
        if not key:
            return self._send_json(400, {"error": "Missing 'key'"})

        success, result = store.read(key)
        if success:
            self._send_json(200, {"key": key, "value": result})
        else:
            self._send_json(404, {"error": result})

    def do_POST(self):
        if self.path != "/store":
            return self._send_json(404, {"error": "Not found"})
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            key = data["key"]
            value = data["value"]
        except (KeyError, json.JSONDecodeError):
            return self._send_json(400, {"error": "Invalid JSON or missing fields"})

        success, result = store.create(key, value)
        code = 201 if success else 400
        self._send_json(code, {"message": result})

    def do_PUT(self):
        if self.path != "/store":
            return self._send_json(404, {"error": "Not found"})
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            key = data["key"]
            value = data["value"]
        except (KeyError, json.JSONDecodeError):
            return self._send_json(400, {"error": "Invalid JSON or missing fields"})

        success, result = store.update(key, value)
        code = 200 if success else 404
        self._send_json(code, {"message": result})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path != "/store":
            return self._send_json(404, {"error": "Not found"})
        params = parse_qs(parsed.query)
        key = params.get("key", [None])[0]
        if not key:
            return self._send_json(400, {"error": "Missing 'key'"})

        success, result = store.delete(key)
        code = 200 if success else 404
        self._send_json(code, {"message": result})

    
def run(server_class=HTTPServer, handler_class=SimpleKVHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()