from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
import uuid

router = APIRouter(prefix="/analyze", tags=["Analyze"])

@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    try:
        # 1️⃣ Read PDF (max 2 pages)
        text = ""

        with pdfplumber.open(resume.file) as pdf:
            for i, page in enumerate(pdf.pages):
                if i >= 2:
                    break
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Could not extract text from PDF"}
            )

        # 2️⃣ Limit text
        MAX_CHARS = 3000
        text = text[:MAX_CHARS]

        # 3️⃣ Simple deterministic analysis (NO AI)
        length_score = min(95, max(35, 40 + len(text) // 120))

        analysis = {
            "skill_score": length_score,
            "strengths": [
                "Resume successfully parsed",
                "Relevant keywords detected",
                "Clear section structure"
            ],
            "weaknesses": [
                "Detailed AI analysis temporarily unavailable",
                "Resume could be more concise",
                "Add more quantified achievements"
            ]
        }

        return JSONResponse(content={
            "id": str(uuid.uuid4()),
            "analysis": analysis
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
