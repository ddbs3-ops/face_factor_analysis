from backend.app.schemas.consultation import RecommendationItem, ConsultationKeyRequest

def build_summary(
    recommendations: list[RecommendationItem],
) -> str:
    active_recommendations = [
        recommendation
        for recommendation in recommendations
        if recommendation.score != 0
    ]

    if not active_recommendations:
        return "전체적으로 특정 요소를 강하게 조절하기보다는 자연스러운 균형을 유지하는 방향이 좋아요."

    elements = [
        recommendation.text
        for recommendation in active_recommendations
    ]

    return "전체적으로 " + ", ".join(elements) + "이 어울려요"

def build_key_requests(
    recommendations: list[RecommendationItem],
) -> list[ConsultationKeyRequest]:
    requests = []

    for recommendation in recommendations:
        sentence = build_consultation_sentence(recommendation)

        if sentence:
            requests.append(
                ConsultationKeyRequest(
                    element=recommendation.element,
                    score=recommendation.score,
                    text=sentence,
                )
            )

    return requests

def build_consultation_sentence(
    recommendation: RecommendationItem,
) -> str:
    element = recommendation.element
    score = recommendation.score

    if element == "top_volume":
        if score > 0:
            return "윗머리는 적당히 볼륨을 살리는 방향으로 하고 싶어요."
        elif score < 0:
            return "윗머리 볼륨은 과하지 않게 자연스럽게 눌러주세요."

    elif element == "side_volume":
        if score > 0:
            return "옆머리는 어느 정도 볼륨이 살아나도록 해주세요."
        elif score < 0:
            return "옆머리는 부피가 많이 뜨지 않게 정리해주세요."

    elif element == "forehead_exposure":
        if score > 0:
            return "이마가 어느 정도 드러나도록 연출해주세요."
        elif score < 0:
            return "앞머리로 이마를 어느 정도 덮는 느낌으로 해주세요."

    elif element == "bangs_length":
        if score > 0:
            return "앞머리는 조금 길게 가져가고 싶어요."
        elif score < 0:
            return "앞머리는 너무 길지 않게 짧고 가볍게 해주세요."

    elif element == "bangs_weight":
        if score > 0:
            return "앞머리는 어느 정도 무게감 있게 잡아주세요."
        elif score < 0:
            return "앞머리는 답답하지 않게 가볍게 해주세요."

    elif element == "parting_asymmetry":
        if score > 0:
            return "가르마는 너무 정가르마보다는 비대칭 느낌으로 해주세요."
        elif score < 0:
            return "가르마는 과한 비대칭보다는 안정적으로 잡아주세요."

    elif element == "curl_strength":
        if score > 0:
            return "컬감은 어느 정도 살려서 부드럽게 표현해주세요."
        elif score < 0:
            return "컬은 과하지 않게 줄이고 비교적 깔끔한 느낌으로 해주세요."

    return ""

def generate_consultation_text(
    recommendations: list[RecommendationItem],
) -> str:
    sentences = []

    for recommendation in recommendations:
        sentence = build_consultation_sentence(recommendation)

        if sentence:
            sentences.append(sentence)

    return " ".join(sentences)