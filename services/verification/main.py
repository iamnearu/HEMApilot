from fastapi import FastAPI

app = FastAPI(title="Verification Service")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "verification"}
