from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
import uuid

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    try:
        # 1️⃣ Read PDF (safe & fast)
        text = ""
        with pdfplumber.open(resume.file) as pdf:
            for page in pdf.pages[:2]:   # HARD LIMIT
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if len(text.strip()) < 50:
            return JSONResponse(
                status_code=400,
                content={"status": "ERROR", "message": "Invalid or empty resume"}
            )

        # 2️⃣ INSTANT ANALYSIS (MVP LOGIC)
        file_id = str(uuid.uuid4())

        return {
            "status": "OK",
            "file_id": file_id,
            "ats_score": 72,
            "summary": "Your resume is readable but needs ATS keyword optimization.",
            "strengths": [
                "Clear education section",
                "Relevant skills listed"
            ],
            "weaknesses": [
                "Lack of quantified achievements",
                "Formatting can be improved"
            ],
            "missing_skills": [
                "Industry-specific tools",
                "ATS keywords"
            ]
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "ERROR", "message": str(e)}
        )
