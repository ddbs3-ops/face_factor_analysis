HAIR_ELEMENTS = [
    "top_volume",
    "side_volume",
    "forehead_exposure",
    "bangs_length",
    "bangs_weight",
    "parting_asymmetry",
    "curl_strength",
]


def get_hair_rules(
    face_measurements,
    quantized_measurements,
):
    rules = []

    vertical_rule = get_vertical_face_rule(
        face_measurements,
        quantized_measurements,
    )

    if vertical_rule is not None:
        rules.append(vertical_rule)

    lower_face_rule = get_lower_face_rule(
        quantized_measurements
    )

    if lower_face_rule is not None:
        rules.append(lower_face_rule)

    return rules


def get_vertical_face_rule(
    face_measurements,
    quantized_measurements,
):
    height_level = quantized_measurements[
        "height_to_width_ratio"
    ]

    if height_level >= 1:
        return get_long_face_rule(
            face_measurements,
            quantized_measurements,
        )

    elif height_level <= -1:
        return get_short_face_rule(
            face_measurements,
            quantized_measurements,
        )

    return None


def get_long_face_rule(
    face_measurements,
    quantized_measurements,
):
    vertical_ratios = {
        "upper": face_measurements.vertical_ratios.upper,
        "middle": face_measurements.vertical_ratios.middle,
        "lower": face_measurements.vertical_ratios.lower,
    }

    dominant_region = max(
        vertical_ratios,
        key=vertical_ratios.get,
    )

    dominant_level = quantized_measurements[
        f"{dominant_region}_ratio"
    ]

    if dominant_region == "upper":
        return {
            "source": "vertical_face",
            "face_type": "long",
            "dominant_region": "upper",
            "feature": "상안부 비율이 상대적으로 큰 긴 얼굴",
            "feature_level": dominant_level,
            "adjustments": {
                "top_volume": -1,
                "side_volume": 1,
                "forehead_exposure": -1,
                "bangs_length": 1,
            },
            "effect": (
                "긴 상안부의 노출을 줄이고 "
                "얼굴의 세로 방향 강조를 완화"
            ),
        }

    elif dominant_region == "middle":
        return {
            "source": "vertical_face",
            "face_type": "long",
            "dominant_region": "middle",
            "feature": "중안부 비율이 상대적으로 큰 긴 얼굴",
            "feature_level": dominant_level,
            "adjustments": {
                "top_volume": -1,
                "side_volume": 1,
                "forehead_exposure": 1,
                "bangs_length": -1,
            },
            "effect": (
                "이마를 노출해 시선을 위쪽으로 분산하고 "
                "중안부의 세로 강조를 완화"
            ),
        }

    else:
        return {
            "source": "vertical_face",
            "face_type": "long",
            "dominant_region": "lower",
            "feature": "하안부 비율이 상대적으로 큰 긴 얼굴",
            "feature_level": dominant_level,
            "adjustments": {
                "top_volume": -1,
                "side_volume": 1,
                "forehead_exposure": 1,
                "bangs_length": -1,
            },
            "effect": (
                "시선을 얼굴 위쪽으로 분산하여 "
                "하안부의 세로 강조를 완화"
            ),
        }


def get_short_face_rule(
    face_measurements,
    quantized_measurements,
):
    vertical_ratios = {
        "upper": face_measurements.vertical_ratios.upper,
        "middle": face_measurements.vertical_ratios.middle,
        "lower": face_measurements.vertical_ratios.lower,
    }

    dominant_region = max(
        vertical_ratios,
        key=vertical_ratios.get,
    )

    dominant_level = quantized_measurements[
        f"{dominant_region}_ratio"
    ]

    if dominant_region == "upper":
        return {
            "source": "vertical_face",
            "face_type": "short",
            "dominant_region": "upper",
            "feature": "상안부 비율이 상대적으로 큰 짧은 얼굴",
            "feature_level": dominant_level,
            "adjustments": {
                "top_volume": 1,
                "side_volume": -1,
                "forehead_exposure": -1,
                "bangs_length": 1,
            },
            "effect": (
                "상안부의 노출을 조절하면서 "
                "전체적으로 세로 방향의 비율을 보완"
            ),
        }

    elif dominant_region == "middle":
        return {
            "source": "vertical_face",
            "face_type": "short",
            "dominant_region": "middle",
            "feature": "중안부 비율이 상대적으로 큰 짧은 얼굴",
            "feature_level": dominant_level,
            "adjustments": {
                "top_volume": 1,
                "side_volume": -1,
                "forehead_exposure": 1,
                "bangs_length": -1,
            },
            "effect": (
                "이마를 노출하고 윗부분의 높이를 보완해 "
                "얼굴의 세로 비율을 늘려 보이게 함"
            ),
        }

    else:
        return {
            "source": "vertical_face",
            "face_type": "short",
            "dominant_region": "lower",
            "feature": "하안부 비율이 상대적으로 큰 짧은 얼굴",
            "feature_level": dominant_level,
            "adjustments": {
                "top_volume": 1,
                "side_volume": -1,
                "forehead_exposure": 1,
                "bangs_length": -1,
            },
            "effect": (
                "시선을 얼굴 위쪽으로 분산하고 "
                "윗부분의 높이를 보완해 세로 비율을 강조"
            ),
        }


def get_lower_face_rule(
    quantized_measurements,
):
    jaw_width_level = quantized_measurements[
        "jaw_to_cheekbone_width_ratio"
    ]

    chin_level = quantized_measurements["chin_angle"]
    left_jaw_level = quantized_measurements["left_jaw_angle"]
    right_jaw_level = quantized_measurements["right_jaw_angle"]

    jaw_angle_level = (
        left_jaw_level + right_jaw_level
    ) / 2

    if jaw_width_level >= 1:
        if chin_level <= -1 and jaw_angle_level <= -1:
            return {
                "source": "lower_face",
                "feature": "광대 대비 턱 폭이 넓고 각진 편",
                "feature_level": jaw_width_level,
                "adjustments": {
                    "forehead_exposure": 1,
                    "bangs_length": -1,
                    "curl_strength": 1,
                },
                "effect": "이마를 드러내고 컬감을 활용해 각진 하안부 인상을 부드럽게 완화",
            }

        return {
            "source": "lower_face",
            "feature": "광대 대비 턱 폭이 넓고 둥근 편",
            "feature_level": jaw_width_level,
            "adjustments": {
                "forehead_exposure": 1,
                "bangs_length": -1,
                "curl_strength": -1,
            },
            "effect": "이마를 드러내고 짧고 직선적인 헤어 요소를 활용해 둥근 하안부의 폭감을 분산",
        }

    elif jaw_width_level <= -1:
        return {
            "source": "lower_face",
            "feature": "광대 대비 턱 폭이 좁고 샤프한 편",
            "feature_level": jaw_width_level,
            "adjustments": {},
            "effect": "하안부 폭에 대한 강한 보정은 필요하지 않음",
        }

    else:
        return None

def merge_hair_rules(rules):
    merged_adjustments = {}

    for rule in rules:
        for element, value in rule["adjustments"].items():
            if element not in merged_adjustments:
                merged_adjustments[element] = 0

            merged_adjustments[element] += value

    return {
        "rules": rules,
        "merged_adjustments": merged_adjustments,
    }

def build_hair_recommendation(merged_adjustments):
    recommendations = []

    recommendation_texts = {
        "top_volume": {
            "positive": "윗머리 볼륨을 살리는 방향",
            "negative": "윗머리 볼륨을 낮추는 방향",
        },
        "side_volume": {
            "positive": "옆머리 볼륨을 살리는 방향",
            "negative": "옆머리 볼륨을 줄이는 방향",
        },
        "forehead_exposure": {
            "positive": "이마를 더 드러내는 방향",
            "negative": "이마 노출을 줄이는 방향",
        },
        "bangs_length": {
            "positive": "앞머리를 길게 가져가는 방향",
            "negative": "앞머리를 짧게 가져가는 방향",
        },
        "bangs_weight": {
            "positive": "앞머리에 무게감을 주는 방향",
            "negative": "앞머리를 가볍게 가져가는 방향",
        },
        "parting_asymmetry": {
            "positive": "가르마를 비대칭적으로 가져가는 방향",
            "negative": "가르마를 대칭적으로 가져가는 방향",
        },
        "curl_strength": {
            "positive": "컬감을 살리는 방향",
            "negative": "컬을 줄이고 직선적인 느낌을 살리는 방향",
        },
    }

    for element in HAIR_ELEMENTS:
        value = merged_adjustments.get(element, 0)

        if value > 0:
            recommendations.append({
                "element": element,
                "score": value,
                "text": recommendation_texts[element]["positive"],
            })

        elif value < 0:
            recommendations.append({
                "element": element,
                "score": value,
                "text": recommendation_texts[element]["negative"],
            })

    return recommendations