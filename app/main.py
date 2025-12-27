from fastapi import FastAPI

app = FastAPI(title="Naukri Pakki API")

@app.get("/")
def root():
    return {"status": "API is running"}
