from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import pdfplumber
import google.generativeai as genai

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

# ---------------------------------------------------
# Load Gemini API key from environment (SAFE)
# ---------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None  # Prevent crash on startup


# ---------------------------------------------------
# Health check route
# ---------------------------------------------------
@router.get("/")
def analyze_test():
    return {"message": "Analyze route is working"}


# ---------------------------------------------------
# Upload + Analyze Resume
# ---------------------------------------------------
@router.post("/upload")
async def upload_and_analyze_resume(file: UploadFile = File(...)):

    # 1️⃣ Validate API key
    if not GEMINI_API_KEY or not model:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key not configured"
        )

    # 2️⃣ Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # 3️⃣ Extract text from PDF
    try:
        text = ""
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to read PDF"
        )

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text found in PDF"
        )

    # 4️⃣ Send to Gemini for analysis
    prompt = f"""
You are an expert HR and ATS resume evaluator.

Analyze the following resume and provide:
1. Resume summary
2. Key skills
3. Strengths
4. Weaknesses
5. ATS score out of 100
6. Improvement suggestions

Resume text:
{text}
"""

    try:
        response = model.generate_content(prompt)
        analysis = response.text
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Gemini analysis failed"
        )

    # 5️⃣ Final response
    return {
        "filename": file.filename,
        "analysis": analysis
    }
