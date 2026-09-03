from fastapi import APIRouter,HTTPException

from backend.app.schemas.consultation import (
    ConsultationGenerateRequest,
    ConsultationGenerateResponse,
    ConsultationShareRequest,
    ConsultationShareResponse,
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

from backend.app.services.consultation_flow_service import (
    load_consultation_flow,
)

router = APIRouter()


@router.post(
    "/consultation/generate",
    response_model=ConsultationGenerateResponse,
)
def create_consultation(
    request: ConsultationGenerateRequest,
) -> ConsultationGenerateResponse:
    summary = build_summary(request.recommendations)

    key_requests = build_key_requests(
        request.recommendations
    )

    consultation_text = generate_consultation_text(
        request.recommendations
    )

    return ConsultationGenerateResponse(
        summary=summary,
        key_requests=key_requests,
        consultation_text=consultation_text,
    )

@router.post(
    "/consultation/share",
    response_model=ConsultationShareResponse,
)
def share_consultation(
    request: ConsultationShareRequest,
) -> ConsultationShareResponse:
    share_id = save_consultation(
        summary=request.summary,
        consultation_text=request.consultation_text,
        personal_request=request.personal_request,
        key_requests=[
            {
                "element": item.element,
                "score": item.score,
                "text": item.text,
            }
            for item in request.key_requests
        ], #db 저장
    )

    return ConsultationShareResponse(
        share_id=share_id,
    ) #공유가능한 id 돌려줌

@router.get("/consultations/{share_id}")
def get_shared_consultation(share_id: str):
    consultation = get_consultation_by_share_id(share_id)

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="상담 결과를 찾을 수 없습니다.",
        )

    return consultation

@router.get("/consultation/flow")
def get_consultation_flow():
    return load_consultation_flow()