from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pdfplumber
import google.generativeai as genai
import os

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

# Gemini setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")


@router.get("/")
def analyze_test():
    return {"message": "Analyze route is working"}


@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    try:
        # 1. Read PDF text
        text = ""
        with pdfplumber.open(resume.file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            raise HTTPException(status_code=400, detail="PDF has no readable text")

        # 2. Prompt
        prompt = f"""
You are an ATS resume analyzer.

Return ONLY valid JSON in this exact format:
{{
  "ats_score": 0-100,
  "strengths": [],
  "weaknesses": [],
  "missing_skills": [],
  "summary": ""
}}

Resume text:
{text}
"""

        # 3. Gemini call
        response = model.generate_content(prompt)

        # 4. SAFE response extract
        if not response or not response.candidates:
            raise Exception("Empty response from Gemini")

        result_text = response.candidates[0].content.parts[0].text

        return JSONResponse(
            content={
                "status": "OK",
                "analysis": result_text
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
