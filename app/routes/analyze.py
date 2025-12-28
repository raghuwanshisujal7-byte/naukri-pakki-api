from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import pdfplumber
import google.generativeai as genai
import asyncio

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

# ----------------------------
# Test route (DO NOT TOUCH)
# ----------------------------
@router.get("/")
def analyze_test():
    return {"message": "Analyze route is working"}

# ----------------------------
# Upload & Analyze Resume
# ----------------------------
@router.post("/upload")
async def upload_and_analyze_resume(file: UploadFile = File(...)):

    # 1️⃣ Validate file
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    # 2️⃣ Read PDF safely (LIMIT TEXT)
    try:
        text = ""
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages[:3]:  # ⛔ LIMIT TO FIRST 3 PAGES
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        text = text[:4000]  # ⛔ HARD LIMIT FOR GEMINI

        if not text.strip():
            raise HTTPException(status_code=400, detail="PDF contains no readable text")

    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read PDF")

    # 3️⃣ Load Gemini API key SAFELY
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key missing")

    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
You are a resume analyzer.

Analyze the following resume text and return:
1. Key skills
2. Weak areas
3. Resume score out of 100
4. Improvement suggestions

Resume:
{text}
"""

    # 4️⃣ CALL GEMINI WITH TIMEOUT (CRITICAL FIX)
    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(model.generate_content, prompt),
            timeout=25  # ⛔ Prevent infinite loading
        )

        return {
            "filename": file.filename,
            "analysis": response.text
        }

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Gemini timeout (free tier). Try smaller PDF."
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini error: {str(e)}"
        )
