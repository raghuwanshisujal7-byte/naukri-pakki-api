from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

# Test route (GET)
@router.get("/")
def analyze_test():
    return {"message": "Analyze route is working"}

# Upload route (POST)
@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    return JSONResponse(
        content={
            "message": "Resume received successfully"
        }
    )

