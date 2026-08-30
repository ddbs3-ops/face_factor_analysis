from fastapi import APIRouter,HTTPException

from backend.app.schemas.consultation import (
    ConsultationRequest,
    ConsultationResponse,
)
from backend.app.services.consultation_service import (
    build_summary,
    build_key_requests,
    generate_consultation_text,
)

from database.consultation_repository import (
    save_consultation,
    get_consultation_by_share_id,
)

router = APIRouter()


@router.post(
    "/consultation",
    response_model=ConsultationResponse,
)
def create_consultation(
    request: ConsultationRequest,
) -> ConsultationResponse:
    summary = build_summary(request.recommendations)

    key_requests = build_key_requests(
        request.recommendations
    )

    consultation_text = generate_consultation_text(
        request.recommendations
    )
    share_id = save_consultation(
        summary=summary,
        consultation_text=consultation_text,
        key_requests=[
            {
                "element": item.element,
                "score": item.score,
                "text": item.text,
            }
            for item in key_requests
        ],
    )

    return ConsultationResponse(
        summary=summary,
        key_requests=key_requests,
        consultation_text=consultation_text,
        share_id=share_id,
    )

@router.get("/consultations/{share_id}")
def get_shared_consultation(share_id: str):
    consultation = get_consultation_by_share_id(share_id)

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="상담 결과를 찾을 수 없습니다.",
        )

    return consultation