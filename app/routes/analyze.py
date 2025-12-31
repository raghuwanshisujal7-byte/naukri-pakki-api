from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

# -------------------------
# TEST ROUTE (GET)
# -------------------------
@router.get("/")
def analyze_test():
    return {"message": "Analyze route is working"}


# -------------------------
# UPLOAD ROUTE (POST)
# PHASE 1 – MOCK RESPONSE
# -------------------------
@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    return JSONResponse(
        content={
            "message": "Resume uploaded successfully",
            "filename": resume.filename,
            "content_type": resume.content_type,
            "status": "OK"
        }
    )
