from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

@router.get("/")
def analyze_test():
    return {"message": "Analyze route is working"}

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "Resume uploaded successfully"
    }
