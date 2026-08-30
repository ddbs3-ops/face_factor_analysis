from fastapi import APIRouter

from backend.app.schemas.consultation import (
    ConsultationRequest,
    ConsultationResponse,
)
from backend.app.services.consultation_service import (
    build_summary,
    build_key_requests,
    generate_consultation_text,
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

    return ConsultationResponse(
        summary=summary,
        key_requests=key_requests,
        consultation_text=consultation_text,
    )