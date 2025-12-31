from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
import google.generativeai as genai
import os

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
        # 1. Read PDF
        text = ""
        with pdfplumber.open(resume.file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

        if len(text.strip()) < 100:
            return JSONResponse(
                status_code=400,
                content={"error": "Resume text too short or unreadable"}
            )

        # 2. AI Prompt
        prompt = f"""
        Analyze the following resume and return:
        1. ATS Score out of 100
        2. Top 5 strengths
        3. Top 5 weaknesses
        4. Missing skills
        5. One-line improvement advice

        Resume:
        {text}
        """

        # 3. Gemini Call
        response = model.generate_content(prompt)

        # 4. Return result
        return {
            "status": "OK",
            "ats_score": "Parsed by AI",
            "analysis": response.text
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
