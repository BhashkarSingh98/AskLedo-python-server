from fastapi import FastAPI

app = FastAPI(
    title="AskLedo Python API",
    description="Phase 1 learning service — hello and health only. Nest remains the product API.",
    version="0.1.0",
)


@app.get("/")
def hello() -> dict[str, str | int]:
    return {
        "message": "Hello from AskLedo Python API",
        "service": "python-api",
        "phase": 1,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
