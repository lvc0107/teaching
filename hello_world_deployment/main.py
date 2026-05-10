from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Hello Deploy", version="1.0.0")

# In-memory counter (resets on restart — enough for this demo)
state = {"count": 0, "started_at": datetime.utcnow().isoformat()}


@app.get("/")
def hello():
    return {
        "message": "Hello World 🚀",
        "env": "DEV",
        "started_at": state["started_at"],
    }


@app.get("/ping")
def ping():
    state["count"] += 1
    return {
        "invocations": state["count"],
        "message": f"This endpoint has been called {state['count']} time(s).",
    }


@app.get("/health")
def health():
    """Used by GitHub Actions and load balancers to verify the service is up."""
    return {"status": "ok"}
