from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.app.services.analysis_service import analyze_uploaded_image


router = APIRouter()


@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    result = await analyze_uploaded_image(file)

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="얼굴 분석에 실패했습니다.",
        )

    return result
