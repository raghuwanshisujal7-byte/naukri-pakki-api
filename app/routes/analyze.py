from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import pdfplumber
import google.generativeai as genai

router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)

# Load Gemini key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


@router.get("/")
def analyze_test():
    return {"message": "Analyze route is working"}


@router.post("/upload")
async def upload_and_analyze_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    # Read PDF text
    text = ""
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text found in PDF")

    # Ask Gemini to analyze resume
    prompt = f"""
    You are a professional HR resume analyzer.

    Analyze the following resume and return:
    1. Candidate profile summary
    2. Key skills
    3. Missing skills
    4. Resume improvement suggestions
    5. Resume score out of 100

    Resume text:
    {text}
    """

    response = model.generate_content(prompt)

    return {
        "filename": file.filename,
        "analysis": response.text
    }
