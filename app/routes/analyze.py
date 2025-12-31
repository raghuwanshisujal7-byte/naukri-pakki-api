from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
import google.generativeai as genai
import os
import json

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

# Gemini setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    try:
        # 1️⃣ Read PDF safely
        text = ""
        with pdfplumber.open(resume.file) as pdf:
            for page in pdf.pages[:3]:   # LIMIT pages (IMPORTANT)
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if len(text.strip()) < 100:
            return JSONResponse(
                status_code=400,
                content={"status": "ERROR", "message": "Resume text too short"}
            )

        # 2️⃣ STRICT PROMPT (JSON ONLY)
        prompt = f"""
You are an ATS resume analyzer.

Return ONLY valid JSON in this format:

{{
  "ats_score": number between 0-100,
  "summary": string,
  "strengths": [string],
  "weaknesses": [string],
  "missing_skills": [string]
}}

Resume text:
{text}
"""

        response = model.generate_content(prompt)

        # 3️⃣ Parse JSON safely
        raw = response.text.strip()

        # Remove markdown if Gemini adds it
        raw = raw.replace("```json", "").replace("```", "").strip()

        result = json.loads(raw)

        # 4️⃣ FINAL RESPONSE
        return {
            "status": "OK",
            "ats_score": result["ats_score"],
            "summary": result["summary"],
            "strengths": result["strengths"],
            "weaknesses": result["weaknesses"],
            "missing_skills": result["missing_skills"]
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "ERROR",
                "message": str(e)
            }
        )

