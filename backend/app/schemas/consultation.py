from pydantic import BaseModel


class RecommendationItem(BaseModel):
    element: str
    score: int
    text: str

class ConsultationKeyRequest(BaseModel):
    element: str
    score: int
    text: str

class ConsultationGenerateResponse(BaseModel):
    summary: str
    key_requests: list[ConsultationKeyRequest]
    consultation_text: str


class ConsultationShareRequest(BaseModel):
    summary: str
    key_requests: list[ConsultationKeyRequest]
    consultation_text: str
    personal_request: str | None = None


class ConsultationShareResponse(BaseModel):
    share_id: str

class ConsultationGenerateRequest(BaseModel):
    recommendations: list[RecommendationItem]
    guided_answers: dict[str, str | list[str]] | None = None