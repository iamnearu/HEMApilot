from fastapi import FastAPI

app = FastAPI(title="Orchestrator Service")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "orchestrator"}
