from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
import google.generativeai as genai
import os, json, uuid, time, random

router = APIRouter(prefix="/analyze", tags=["Analyze"])

# 🔑 Gemini config
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def call_gemini(prompt: str) -> str:
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.7,       # variation (no same result)
            "max_output_tokens": 600
        }
    )
    return response.text


@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    try:
        # 🟢 STEP 1: Read PDF (limit pages)
        text = ""
        with pdfplumber.open(resume.file) as pdf:
            for i, page in enumerate(pdf.pages):
                if i >= 2:   # max 2 pages only
                    break
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Unable to extract text from PDF"}
            )

        # 🧪 DEBUG (optional)
        print("Resume length:", len(text))

        # 🟢 STEP 2: STRONG PROMPT (no same % issue)
        prompt = f"""
You are an expert ATS resume analyzer.

Analyze the resume below carefully.

Resume Text:
{text}

IMPORTANT RULES:
- Score must be realistic between 35 and 95
- Each resume MUST produce different score
- Strengths and weaknesses must depend on resume content
- Do NOT repeat same generic points

Return STRICT JSON only in this format:

{{
  "skill_score": number,
  "strengths": ["point 1", "point 2", "point 3"],
  "weaknesses": ["point 1", "point 2", "point 3"]
}}
"""

        # 🟢 STEP 3: Call Gemini
        raw_response = call_gemini(prompt)

        # 🟢 STEP 4: Parse JSON safely
        try:
            analysis = json.loads(raw_response)
        except Exception:
            # 🔒 Fallback
