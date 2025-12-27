from fastapi import APIRouter

router = APIRouter(prefix="/analyze", tags=["Analyze"])

@router.get("/")
def analyze_test():
    return {"message": "Analyze route is working"}
