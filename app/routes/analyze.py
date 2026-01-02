from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
import docx
import io

router = APIRouter()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])


@router.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()

        if file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
        elif file.filename.endswith(".docx"):
            text = extract_text_from_docx(file_bytes)
        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Only PDF or DOCX allowed"}
            )

        # 🔹 SIMPLE DEMO ANALYSIS (abhi)
        word_count = len(text.split())
        score = min(100, max(30, word_count // 10))

        skills = []
        keywords = ["python", "java", "flask", "fastapi", "machine learning", "ai"]
        for k in keywords:
            if k.lower() in text.lower():
                skills.append(k)

        return {
            "success": True,
            "score": score,
            "skills": skills,
            "words": word_count
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
