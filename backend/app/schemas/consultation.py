from pydantic import BaseModel


class RecommendationItem(BaseModel):
    element: str
    score: int
    text: str


class ConsultationRequest(BaseModel):
    recommendations: list[RecommendationItem]


class ConsultationResponse(BaseModel):
    summary: str
    key_requests: list[str]
    consultation_text: str