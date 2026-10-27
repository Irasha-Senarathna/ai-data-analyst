"""FastAPI entry point."""

from fastapi import FastAPI

app = FastAPI(title="AI Data Analyst API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check used by Docker Compose and CI."""
    return {"status": "ok"}
