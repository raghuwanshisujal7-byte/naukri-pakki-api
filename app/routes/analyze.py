from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
import google.generativeai as genai
import os
import json
import uuid

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

# ================================
# Gemini CONFIG (IMPORTANT)
# ================================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config={
        "temperature": 0.85,        # DIFFERENT RESULT EVERY TIME
        "top_p": 0.95,
        "max_output_tokens": 900
    }
)

# ================================
# ANALYZE RESUME API
# ================================
@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    try:
        # ----------------------------
        # 1️⃣ READ PDF (LIMITED PAGES)
        # ----------------------------
        text = ""
        with pdfplumber.open(resume.file) as pdf:
            for page in pdf.pages[:3]:   # only first 3 pages
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if len(text.strip()) < 100:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "ERROR",
                    "message": "Resume content too short or unreadable"
                }
            )

        # ----------------------------
        # 2️⃣ STRONG UNIQUE PROMPT
        # ----------------------------
        prompt = f"""
You are a professional ATS resume evaluator.

Analyze the resume and return ONLY valid JSON.
Do NOT repeat previous answers.
Base your evaluation strictly on the resume content.

JSON FORMAT:
{{
  "ats_score": number between 0 and 100,
  "summary": string,
  "strengths": [string, string],
  "weaknesses": [string, string],
  "missing_skills": [string, string]
}}

Resume:
{text}
"""

        response = model.generate_content(prompt)

        # ----------------------------
        # 3️⃣ SAFE JSON PARSING
        # ----------------------------
        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        result = json.loads(raw)

        # ----------------------------
        # 4️⃣ FINAL RESPONSE
        # ----------------------------
        return {
            "status": "OK",
            "file_id": str(uuid.uuid4()),
            "ats_score": result.get("ats_score"),
            "summary": result.get("summary"),
            "strengths": result.get("strengths"),
            "weaknesses": result.get("weaknesses"),
            "missing_skills": result.get("missing_skills")
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "ERROR",
                "message": str(e)
            }
        )
