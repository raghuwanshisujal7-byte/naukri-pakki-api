from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
import os
import google.generativeai as genai

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

# -------------------------
# CONFIG
# -------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# -------------------------
# TEST ROUTE
# -------------------------
@router.get("/")
def analyze_test():
    return {"message": "Analyze route is working"}

# -------------------------
# ANALYZE RESUME (POST)
# -------------------------
@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    try:
        # 1️⃣ Extract text from PDF
        resume_text = ""
        with pdfplumber.open(resume.file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    resume_text += text + "\n"

        if not resume_text.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Could not extract text from PDF"}
            )

        # 2️⃣ Gemini Prompt
        prompt = f"""
You are an ATS resume analyzer.

Analyze the following resume and return STRICT JSON only in this format:

{{
  "ats_score": number between 0-100,
  "strengths": [list of strengths],
  "weaknesses": [list of weaknesses],
  "missing_skills": [list of missing skills],
  "summary": "short improvement summary"
}}

Resume Text:
{resume_text}
"""

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        analysis_text = response.text.strip()

        # 3️⃣ Return raw AI response (Phase 2)
        return JSONResponse(
            content={
                "message": "Resume analyzed successfully",
                "analysis_raw": analysis_text
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
