# KeyValueStorePhysicsX (Python Standard Library Only)

This is a simple in-memory key-value store written in pure Python. It supports basic CRUD operations via an HTTP interface.

---

## Features

- In-memory key-value store
- HTTP API (using `http.server`)
- Thread-safe access with `threading.Lock`
- Key expiration with TTL (Time To Live)
- Logging support for all operations
- Docker support
- Unit tests using `unittest`, including multi-threaded and TTL scenarios
- No external dependencies — standard library only

---

## Getting Started

### Run Locally

```bash
python3 server.py
```

### TEST IT
```bash
curl -X POST http://localhost:8080/store -d '{"key":"P", "value":"PhysicsX"}' -H "Content-Type: application/json"
curl "http://localhost:8080/store?key=P"
curl -X PUT http://localhost:8080/store -d '{"key":"P", "value":"PhysicsXKeyValueStore"}' -H "Content-Type: application/json"
curl -X DELETE "http://localhost:8080/store?key=P"
```

### Run with Docker
```bash
docker build -t kvstore .
docker run -p 8080:8080 kvstore
```

### Running Tests
```bash
python3 test_kv_store.py
```

### TTL Support
- You can set TTL (in seconds) for any key at creation:
```bash
curl -X POST http://localhost:8080/store \
  -d '{"key":"session", "value":"PhysicsX", "ttl":3}' \
  -H "Content-Type: application/json"
```
- After ttl seconds, the key expires and behaves as if it doesn't exist.
- TTL is checked during read/update/delete (lazy cleanup)


### API Endpoints
| Method | Endpoint         | Description           |
| ------ | ---------------- | --------------------- |
| POST   | `/store`         | Create key-value pair |
| GET    | `/store?key=P` | Retrieve value        |
| PUT    | `/store`         | Update value          |
| DELETE | `/store?key=P` | Delete key            |


### Production Considerations
If this were being prepared for real production use, we should:
- Use persistent storage (e.g. SQLite or a file)
- Add thread-safety with locks or queues (threading.Lock - ✅ [Done]) (Allow Configurations to be Read-Write Heavy)
- Support request logging and error tracing (✅ [Done])
- Add graceful shutdown handling (signal module)
- Add authentication/authorization
- Support for TTL (time-to-live) on keys (✅[Done] )
- Switch to async with asyncio and aiohttp or similar (if allowed to use third-party libs)

### Project Structure
`kv_store/`
 - `kv_store.py`          # In-memory store logic
 - `server.py`            # HTTP server using standard library
 - `test_kv_store.py`     # Unit tests
 - `Dockerfile`           # Docker setup
 - `README.md`           # You're reading it

### Author
- Shivam Soni
- Email: sonishivama@gmail.com
- [LinkedIn](https://linkedin.com/in/sonishivama)