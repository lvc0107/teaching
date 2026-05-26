import httpx
import asyncio
"""
Why use httpx instead of requests for sync code?
Even if you don't need asyncio, httpx offers modern features
that requests lacks:
HTTP/2 Support: Ability to use the faster HTTP/2 protocol.
Strict Timeouts: Timeouts are turned on by default (unlike requests).
Type Annotations: Better autocompletion in editors like VS Code or PyCharm.
Compatibility: If you ever decide to go async later, 
the API remains almost identical.
make sure to install the extra dependency with pip install httpx[http2] 
and initialize your client like this:client = httpx.Client(http2=True)
"""

# Use a context manager to ensure connections are closed
with httpx.Client() as client:
    # Multiple calls using the same client
    res1 = client.get("https://httpbin.org")
    res2 = client.post("https://httpbin.org", json={"data": "test"})

    print(res1.status_code)
    print(res2.json())



async def main():
    # Usar un cliente para reutilizar conexiones
    async with httpx.AsyncClient() as client:
        # Petición GET
        response = await client.get("https://httpbin.org")

        # Petición POST con datos JSON
        payload = {"usuario": "python_dev"}
        post_res = await client.post("https://httpbin.org", json=payload)

        print(f"GET Status: {response.status_code}")
        print(f"POST JSON: {post_res.json()['json']}")


if __name__ == "__main__":
    asyncio.run(main())


"""
[ BROWSER / MOBILE APP ]

      |
      | Protocol: HTTP/3 (QUIC/UDP)  <-- Eliminates Head-of-Line blocking
      v
[ REVERSE PROXY / GATEWAY ] (Traefik / Nginx)

      |
      | Task: SSL Termination + Compression
      | Protocol: H2C (HTTP/2 Cleartext) to internal services
      v
[ ASGI SERVER ] (Hypercorn) better than Uvicorn for HTTP/3 support
      |
      | Task: Protocol Translation (HTTP to Python ASGI)
      | Mode: Multi-worker (1 per CPU core)
      v
[ EVENT LOOP ] (uvloop)  <-- THE ENGINE (C/libuv) better than default asyncio loop
      |
      | Task: Scheduling thousands of concurrent I/O tasks
      v
[ WEB FRAMEWORK ] (FastAPI)
      |
      | Logic: Asynchronous path handling (async def)
      v
[ DATA VALIDATION ] (Pydantic V2)   <-- THE CORE (Rust)
      |
      | Task: Blazing fast JSON-to-Object conversion
      v
[ DB DRIVER ] (asyncpg / redis-py)
      |
      | Task: Non-blocking binary communication with DB
      v
[ DATABASE ] (PostgreSQL / Redis)

"""


"""
The Fallback (When things fail)If the HTTP/3 connection fails (e.g., a corporate firewall blocks UDP port 443), the browser falls back to HTTP/2:text[ BROWSER ]

    |
    |-- 1. Tries HTTP/3 (UDP) --> [ FIREWALL / SERVER ]
    |                                 |
    | <--- 2. Blocked or Timeout -----|
    |

    |-- 3. Immediate Fallback --> [ SERVER ]
    |      (HTTP/2 over TCP)
    |

    | <--- 4. Data Received ----------|


"""
