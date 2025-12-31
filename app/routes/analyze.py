from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
import os
import openai

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

# -------------------------
# TEST ROUTE
# -------------------------
@router.get("/")
def analyze_test():
    return {"message": "Analyze route is working"}

# -------------------------
# ANALYZE RESUME (PHASE 3)
# -------------------------
@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    if resume.content_type != "application/pdf":
        return JSONResponse(
            status_code=400,
            content={"error": "Only PDF files are allowed"}
        )

    # Save temp file
    file_path = f"/tmp/{resume.filename}"
    with open(file_path, "wb") as f:
        f.write(await resume.read())

    # Extract text from PDF
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    os.remove(file_path)

    # -------- MOCK AI ANALYSIS (next step real AI) --------
    analysis = {
        "ats_score": 62,
        "strengths": [
            "Clear project descriptions",
            "Relevant technical skills"
        ],
        "weaknesses": [
            "Missing quantified achievements",
            "No summary section"
        ],
        "missing_skills": [
            "System Design",
            "Cloud Basics"
        ]
    }

    return {
        "message": "Resume analyzed successfully",
        "analysis": analysis
    }
