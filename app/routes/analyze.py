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

# Gemini config
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

@router.get("/")
def analyze_test():
    return {"message": "Analyze route is working"}

@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    # 1. Extract text from PDF
    text = ""
    with pdfplumber.open(resume.file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()

    # 2. Prompt Gemini (STRICT JSON)
    prompt = f"""
You are an ATS resume analyzer.

Analyze the resume text below and respond ONLY in valid JSON.

JSON format:
{{
  "ats_score": number (0-100),
  "strengths": [string, string],
  "weaknesses": [string, string],
  "missing_skills": [string, string],
  "summary": string
}}

Resume Text:
{text}
"""

    response = model.generate_content(prompt)
    raw_output = response.text.strip()

    # 3. Convert Gemini output to JSON
    try:
        analysis = json.loads(raw_output)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "error": "AI response not valid JSON",
                "raw_output": raw_output
            }
        )

    # 4. Final response
    return JSONResponse(
        content={
            "message": "Resume analyzed successfully",
            "analysis": analysis
        }
    )

