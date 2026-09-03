import json
from pathlib import Path


FLOW_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "consultation_flow.json"
)


def load_consultation_flow():
    with FLOW_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)

def resolve_guided_answers(
    answers: dict[str, str | list[str]]
) -> dict[str, str | list[str]]:
    flow = load_consultation_flow()

    resolved_answers = {}

    for node_id, answer in answers.items():
        node = flow["nodes"].get(node_id)

        if not node:
            continue

        node_type = node.get("type")

        # 직접 입력 질문
        if node_type == "text":
            resolved_answers[node_id] = answer
            continue

        options = node.get("options", [])

        # single
        if isinstance(answer, str):
            matched_option = next(
                (
                    option
                    for option in options
                    if option["value"] == answer
                ),
                None,
            )

            if matched_option:
                resolved_answers[node_id] = matched_option["label"]

        # multi
        elif isinstance(answer, list):
            labels = [
                option["label"]
                for option in options
                if option["value"] in answer
            ]

            resolved_answers[node_id] = labels

    return resolved_answers


def build_guided_consultation_sentences(
    answers: dict[str, str | list[str]],
) -> list[str]:
    sentences = []

    # 원하는 커트 스타일
    style = answers.get("cut_style_select")
    custom_style = answers.get("cut_style_custom")

    if custom_style:
        sentences.append(
            f"{custom_style} 스타일을 원해요."
        )
    elif style:
        sentences.append(
            f"{style} 스타일을 원해요."
        )

    # 머리를 기르는 중인지
    if answers.get("cut_growing_hair") == "네, 머리를 기르고 있어요":
        sentences.append(
            "현재 머리를 기르고 있어서 전체 길이는 가능한 유지하고 싶어요."
        )

    # 앞머리
    bangs_style = answers.get("cut_bangs_style")
    bangs_detail = (
        answers.get("cut_bangs_up_style")
        or answers.get("cut_bangs_part_style")
        or answers.get("cut_bangs_down_style")
    )
    bangs_length = answers.get("cut_bangs_length")

    if bangs_style:
        bangs_sentence = f"앞머리는 {bangs_style}"

        if bangs_detail:
            bangs_sentence += f", {bangs_detail} 느낌으로"

        if bangs_length:
            bangs_sentence += f" 하고 길이는 {bangs_length} 정도로"

        bangs_sentence += " 해주세요."

        sentences.append(bangs_sentence)

    # 옆머리
    side_style = answers.get("cut_side_section_style")
    two_block_length = answers.get("cut_two_block_length")

    if side_style:
        if two_block_length:
            sentences.append(
                f"옆머리는 {side_style}으로 하고 길이는 {two_block_length}로 정리해주세요."
            )
        else:
            sentences.append(
                f"옆머리는 {side_style}으로 정리해주세요."
            )

    # 다운펌
    down_perm = answers.get("cut_down_perm")

    if down_perm:
        sentences.append(
            f"{down_perm}"
        )

    # 뒷머리
    back_style = (
        answers.get("cut_back_long_style")
        or answers.get("cut_back_short_style")
    )

    if back_style:
        sentences.append(
            f"뒷머리는 {back_style}로 해주세요."
        )

    # 평소 스타일링
    styling_method = answers.get("cut_styling_method")

    if styling_method:
        sentences.append(
            f"평소에는 {styling_method}"
        )

    products = answers.get("cut_styling_products")

    if isinstance(products, list) and products:
        sentences.append(
            f"주로 사용하는 제품은 {', '.join(products)}예요."
        )

    return sentences