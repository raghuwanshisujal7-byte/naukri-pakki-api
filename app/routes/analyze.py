from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import os
import shutil
import uuid

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ Test route
@router.get("/")
def analyze_test():
    return {"message": "Analyze route is working"}

# ✅ SAFE UPLOAD ONLY (NO AI CALL)
@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    try:
        file_id = f"{uuid.uuid4()}_{resume.filename}"
        file_path = os.path.join(UPLOAD_DIR, file_id)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

        return JSONResponse(
            status_code=200,
            content={
                "status": "OK",
                "message": "Resume uploaded successfully",
                "file_id": file_id,
                "next_step": "AI analysis coming soon"
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "ERROR",
                "message": str(e)
            }
        )
