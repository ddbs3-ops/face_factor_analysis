from pydantic import BaseModel


class RecommendationItem(BaseModel):
    element: str
    score: int
    text: str


class ConsultationRequest(BaseModel):
    recommendations: list[RecommendationItem]

class ConsultationKeyRequest(BaseModel):
    element: str
    score: int
    text: str

class ConsultationResponse(BaseModel):
    summary: str
    key_requests: list[ConsultationKeyRequest]
    consultation_text: str
    share_id: str