from fastapi import APIRouter, UploadFile, File, HTTPException
from pypdf import PdfReader

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

@router.get("/")
def analyze_test():
    return {"message": "Analyze route is working"}

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    # 1. Validate file
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    # 2. Extract text from PDF
    try:
        reader = PdfReader(file.file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read PDF")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text found in PDF")

    # 3. Return preview (AI comes next)
    return {
        "filename": file.filename,
        "resume_text_preview": text[:500],
        "message": "PDF read successfully, ready for AI analysis"
    }
