from fastapi import FastAPI
from app.routes.analyze import router as analyze_router

app = FastAPI(title="Naukri Pakki API")

app.include_router(analyze_router)

@app.get("/")
def root():
    return {"status": "API is running"}
