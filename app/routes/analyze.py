from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
import google.generativeai as genai
import os
import json
import uuid

router = APIRouter(prefix="/analyze", tags=["Analyze"])

# 🔐 Gemini config
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def call_gemini(prompt: str) -> str:
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": 500
        }
    )
    return response.text if response and response.text else ""

@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    try:
        # 1️⃣ Read PDF safely (max 2 pages)
        text = ""

        with pdfplumber.open(resume.file) as pdf:
            for i, page in enumerate(pdf.pages):
                if i >= 2:
                    break
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # 🔥 LIMIT resume text length (prevent timeout)
        MAX_CHARS = 3500
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS]

        if not text.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Could not extract text from PDF"}
            )

        # 2️⃣ Build prompt (STRICT + SHORT)
        prompt = f"""
You are an expert resume reviewer.

IMPORTANT RULES:
- Score must be realistic between 35 and 95
- Each resume MUST produce a different score
- Strengths and weaknesses must depend on resume content
- Do NOT repeat generic points

Return STRICT JSON only in this format:

{{
  "skill_score": number,
  "strengths": ["point 1", "point 2", "point 3"],
  "weaknesses": ["point 1", "point 2", "point 3"]
}}

Resume:
{text}
"""

        # 3️⃣ Call Gemini
        raw_response = call_gemini(prompt)

        # 🔐 Fallback if Gemini is slow / empty
        if not raw_response or len(raw_response) < 20:
            return JSONResponse(content={
                "id": str(uuid.uuid4()),
                "analysis": {
                    "skill_score": 60,
                    "strengths": ["Resume uploaded successfully"],
                    "weaknesses": ["AI analysis timed out, showing fallback result"]
                }
            })

        # 4️⃣ Parse JSON safely
        try:
            analysis = json.loads(raw_response)
        except Exception:
            analysis = {
                "skill_score": min(95, max(35, 35 + len(text) // 120)),
                "strengths": ["Relevant experience detected"],
                "weaknesses": ["Resume formatting can be improved"]
            }

        # 5️⃣ Final response
        return JSONResponse(content={
            "id": str(uuid.uuid4()),
            "analysis": analysis
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
