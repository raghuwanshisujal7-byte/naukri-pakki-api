from fastapi import APIRouter, UploadFile, File, HTTPException
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
# UPLOAD & ANALYZE (POST)
# -------------------------
@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):

    # 1. Validate file type
    if resume.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # 2. (Phase 2) Just confirm upload – no AI yet
    return JSONResponse(
        content={
            "message": "Resume uploaded successfully",
            "filename": resume.filename,
            "status": "OK"
        }
    )
