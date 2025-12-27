from fastapi import APIRouter

router = APIRouter()

@router.get("/analyze")
def analyze():
    return {"message": "Analyze route working"}
