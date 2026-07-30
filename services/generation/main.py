from fastapi import FastAPI

app = FastAPI(title="Generation Service")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "generation"}
