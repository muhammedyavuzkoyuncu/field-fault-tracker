from fastapi import FastAPI

app = FastAPI(title="Field Fault Tracker API")


@app.get("/health")
def health():
    return {"status": "ok"}