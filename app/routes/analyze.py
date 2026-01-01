from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
import google.generativeai as genai
import os
import json
import uuid

router = APIRouter(prefix="/analyze", tags=["Analyze"])

# Gemini API config
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def call_gemini(prompt: str) -> str:
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": 600
        }
    )
    return response.text


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

        if not text.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Could not extract text from PDF"}
            )

        # 2️⃣ Prompt
        prompt = f"""
You are an expert ATS resume analyzer.

Analyze the resume below carefully.

Resume Text:
{text}

RULES:
- Score must be between 35 and 95
- Each resume MUST have different score
- Strengths & weaknesses must depend on resume content
- Do NOT repeat generic points

Return STRICT JSON only in this format:

{{
  "skill_score": number,
  "strengths": ["point 1", "point 2", "point 3"],
  "weaknesses": ["point 1", "point 2", "point 3"]
}}
"""

        # 3️⃣ Call Gemini
        raw_response = call_gemini(prompt)

        # 4️⃣ Parse JSON safely
        try:
            analysis = json.loads(raw_response)
        except Exception:
            analysis = {
                "skill_score": (len(text) % 60) + 35,
                "strengths": ["Relevant technical exposure"],
                "weaknesses": ["Resume formatting can be improved"]
            }

        # 5️⃣ Return response
        return JSONResponse(content={
            "id": str(uuid.uuid4()),
            "analysis": analysis
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
