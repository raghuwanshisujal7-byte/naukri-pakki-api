from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
import google.generativeai as genai
import os, json, uuid, time

router = APIRouter(prefix="/analyze", tags=["Analyze"])

# Gemini config
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def call_gemini(prompt: str):
    model = genai.GenerativeModel("gemini-pro")
    return model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.9,          # 🔥 IMPORTANT (variation)
            "max_output_tokens": 600     # 🔥 SPEED CONTROL
        }
    )

@router.post("/")
async def analyze_resume(resume: UploadFile = File(...)):
    try:
        # 1️⃣ Read PDF (limit pages + chars)
        text = ""
        with pdfplumber.open(resume.file) as pdf:
            for page in pdf.pages[:3]:
                t = page.extract_text()
                if t:
                    text += t + "\n"

        text = text.strip()[:4000]  # 🔥 VERY IMPORTANT

        if len(text) < 150:
            return JSONResponse(
                status_code=400,
                content={"status": "ERROR", "message": "Resume content too short"}
            )

        # 2️⃣ UNIQUE PROMPT (resume-dependent)
        prompt = f"""
You are an ATS resume analyzer.

IMPORTANT RULES:
- Different resumes MUST give different ATS scores
- Score must depend strictly on resume content
- Penalize missing skills, missing numbers, weak keywords
- Do NOT repeat generic answers

Scoring logic:
- Start at 100
- Minus points for:
  - No quantified achievements
  - Missing role-specific keywords
  - Poor formatting
  - Generic content

Return ONLY valid JSON in this format (no markdown):

{{
  "ats_score": number (0-100),
  "summary": string,
  "strengths": [string],
  "weaknesses": [string],
  "missing_skills": [string]
}}

Resume text:
{text}
"""

        response = call_gemini(prompt)

        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        result = json.loads(raw)

        # 3️⃣ Safety guard (avoid stuck values)
        score = int(result.get("ats_score", 50))
        score = max(35, min(score, 90))

        return {
            "status": "OK",
            "file_id": str(uuid.uuid4()),
            "ats_score": score,
            "summary": result.get("summary", ""),
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "missing_skills": result.get("missing_skills", [])
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "ERROR", "message": str(e)}
        )
