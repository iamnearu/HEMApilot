from fastapi import FastAPI

app = FastAPI(title="Media Service")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "media"}
