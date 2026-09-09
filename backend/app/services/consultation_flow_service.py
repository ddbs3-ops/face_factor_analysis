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

        def resolve_option_label(option):
            custom_input = option.get("custom_input")
            if custom_input:
                answer_key = custom_input["answer_key"]
                custom_value = answers.get(answer_key)
                if isinstance(custom_value, str) and custom_value.strip():
                    resolved_answers[answer_key] = custom_value.strip()
                    return custom_value.strip()
            return option["label"]

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
                resolved_answers[node_id] = resolve_option_label(matched_option)

        # multi
        elif isinstance(answer, list):
            selected_options = [option for option in options if option["value"] in answer]
            exclusive_options = [option for option in selected_options if option.get("exclusive")]
            if exclusive_options:
                selected_options = exclusive_options[:1]
            labels = [
                resolve_option_label(option)
                for option in selected_options
            ]

            resolved_answers[node_id] = labels

    return resolved_answers


def build_guided_consultation_sentences(
    answers: dict[str, str | list[str]],
) -> list[str]:
    sentences = []

    def as_sentence(text: str) -> str:
        text = text.strip()
        return text if text.endswith((".", "!", "?", "。", "！", "？")) else f"{text}."

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

    # 원하는 스타일을 아직 정하지 못한 고객의 현재 고민
    concern = answers.get("cut_dont_know")
    if isinstance(concern, str) and concern:
        sentences.append(
            "현재 머리에서 특별히 불편한 점은 없어요."
            if concern == "딱히 없어요" else as_sentence(concern)
        )

    avoid_styles = answers.get("cut_avoid_styles")
    if isinstance(avoid_styles, list) and avoid_styles:
        custom_avoid = answers.get("cut_avoid_styles_custom")
        selected_styles = [item for item in avoid_styles if item != custom_avoid]
        if selected_styles:
            sentences.append(f"{', '.join(selected_styles)} 같은 스타일은 피하고 싶어요.")
        if isinstance(custom_avoid, str) and custom_avoid in avoid_styles:
            sentences.append(f"피하고 싶은 내용을 직접 적었어요: “{custom_avoid}”")

    # 머리를 기르는 중인지
    growing_hair = answers.get("cut_growing_hair_undecided", answers.get("cut_growing_hair"))
    if growing_hair == "네, 머리를 기르고 있어요":
        sentences.append(
            "현재 머리를 기르고 있어서 전체 길이는 최대한 유지하고 싶어요."
        )

    considerations = answers.get("cut_hair_considerations")
    if isinstance(considerations, list) and considerations:
        if considerations == ["특별히 없어요"]:
            sentences.append("머리 특징과 관련해 특별히 고려해 주실 부분은 없어요.")
        else:
            custom_consideration = answers.get("cut_hair_considerations_custom")
            features = [item for item in considerations if item != custom_consideration]
            if features:
                sentences.append(f"{', '.join(features)} 같은 특징을 고려해서 커트해 주세요.")
            if isinstance(custom_consideration, str) and custom_consideration in considerations:
                sentences.append(f"이 부분도 함께 고려해 주세요: “{custom_consideration}”")

    change_level = answers.get("cut_change_level")
    if isinstance(change_level, str) and change_level:
        sentences.append(as_sentence(change_level))

    # 앞머리
    bangs_style = answers.get("cut_bangs_style")
    bangs_detail = (
        answers.get("cut_bangs_up_style")
        or answers.get("cut_bangs_part_style")
        or answers.get("cut_bangs_down_style")
    )
    bangs_length = answers.get("cut_bangs_length")

    if bangs_style:
        sentences.append(f"앞머리는 {bangs_style} 스타일로 하고 싶어요.")
        if answers.get("cut_bangs_down_style"):
            sentences.append(f"앞머리 무게감은 {bangs_detail} 해주세요.")
        elif bangs_detail:
            sentences.append(f"앞머리는 {bangs_detail}로 연출하고 싶어요.")

        if bangs_length == "잘 모르겠어요":
            sentences.append("앞머리 길이는 아직 잘 모르겠어요.")
        elif bangs_length == "현재 길이 최대한 유지":
            sentences.append("앞머리는 현재 길이를 최대한 유지해 주세요.")
        elif bangs_length:
            sentences.append(f"앞머리 길이는 {bangs_length} 정도로 맞춰 주세요.")

    # 옆머리
    side_style = answers.get("cut_side_section_style")
    two_block_length = answers.get("cut_two_block_length")

    if side_style:
        if two_block_length:
            sentences.append(
                f"옆머리는 {side_style} 스타일로, 길이는 {two_block_length}로 정리해 주세요."
            )
        else:
            sentences.append(
                f"옆머리는 {side_style} 스타일로 정리해 주세요."
            )

    # 다운펌
    down_perm = answers.get("cut_down_perm")

    if down_perm:
        sentences.append(
            as_sentence(down_perm)
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

    # 펌 상담: 직접 입력한 스타일을 선택지보다 우선해서 전달한다.
    perm_style = answers.get("perm_style_custom") or answers.get("perm_style_select")
    if isinstance(perm_style, str) and perm_style and perm_style != "여기에 없어요":
        sentences.append(f"{perm_style} 스타일을 원해요.")

    part_preference = answers.get("perm_part_preference")
    if isinstance(part_preference, str) and part_preference:
        sentences.append(
            "가르마는 어떻게 할지 아직 잘 모르겠어요."
            if part_preference == "잘 모르겠어요" else as_sentence(part_preference)
        )

    curl_intensity = answers.get("perm_curl_intensity")
    if isinstance(curl_intensity, str) and curl_intensity:
        sentences.append(f"펌은 {curl_intensity} 해주세요.")

    perm_down_perm = answers.get("perm_down_perm")
    if isinstance(perm_down_perm, str) and perm_down_perm:
        sentences.append(as_sentence(perm_down_perm))

    perm_avoid_styles = answers.get("perm_avoid_styles")
    if isinstance(perm_avoid_styles, list) and perm_avoid_styles:
        custom_avoid = answers.get("perm_avoid_styles_custom")
        selected_styles = [item for item in perm_avoid_styles if item != custom_avoid]
        if selected_styles:
            sentences.append(f"{', '.join(selected_styles)} 등은 피하고 싶어요.")
        if isinstance(custom_avoid, str) and custom_avoid in perm_avoid_styles:
            sentences.append(f"피하고 싶은 내용을 직접 적었어요: “{custom_avoid}”")

    # 원하는 펌 스타일을 아직 정하지 못한 경로는 질문 순서대로 전달한다.
    undecided_avoid = answers.get("perm_avoid_styles_undecided")
    if isinstance(undecided_avoid, list) and undecided_avoid:
        if undecided_avoid == ["특별히 없음"]:
            sentences.append("특별히 피하고 싶은 펌 느낌은 없어요.")
        else:
            custom_avoid = answers.get("perm_avoid_styles_undecided_custom")
            selected_styles = [item for item in undecided_avoid if item != custom_avoid]
            if selected_styles:
                sentences.append(f"{', '.join(selected_styles)} 등은 피하고 싶어요.")
            if isinstance(custom_avoid, str) and custom_avoid in undecided_avoid:
                sentences.append(f"피하고 싶은 내용을 직접 적었어요: “{custom_avoid}”")

    perm_reason = answers.get("perm_reason")
    if isinstance(perm_reason, str) and perm_reason:
        sentences.append(as_sentence(perm_reason))

    undecided_part = answers.get("perm_part_preference_undecided")
    part_sentences = {
        "좋아요": "가르마가 있는 스타일도 좋아요.",
        "없는 쪽이 좋아요": "가르마가 없는 스타일이 좋아요.",
        "상관없어요": "가르마 유무는 상관없어요.",
    }
    if isinstance(undecided_part, str) and undecided_part in part_sentences:
        sentences.append(part_sentences[undecided_part])

    undecided_down_perm = answers.get("perm_down_perm_undecided")
    down_perm_sentences = {
        "네": "다운펌도 함께 하고 싶어요.",
        "아니요": "다운펌은 하지 않을게요.",
        "미용사님 추천에 맡길게요": "다운펌 여부는 미용사님 추천에 맡길게요.",
    }
    if isinstance(undecided_down_perm, str) and undecided_down_perm in down_perm_sentences:
        sentences.append(down_perm_sentences[undecided_down_perm])

    perm_change_level = answers.get("perm_change_level")
    if isinstance(perm_change_level, str) and perm_change_level:
        sentences.append(
            as_sentence(perm_change_level) if perm_change_level == "크게 바뀌어도 괜찮아요"
            else f"{perm_change_level} 해주세요."
        )

    # 커트·펌 공통 평소 스타일링
    styling_method = answers.get("styling_method")
    if styling_method:
        sentences.append(as_sentence(f"평소에는 {styling_method}"))

    tools = answers.get("styling_tools")
    if isinstance(tools, list) and tools:
        sentences.append(f"평소 손질할 때 {', '.join(tools)} 등을 사용해요.")

    products = answers.get("styling_products")
    if isinstance(products, list) and products:
        sentences.append(f"헤어 제품은 {', '.join(products)} 등을 사용해요.")

    return sentences
