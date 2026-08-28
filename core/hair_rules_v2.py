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

    face_height_rule = get_face_height_ratio_rule(
        quantized_measurements
    )

    if face_height_rule is not None:
        rules.append(face_height_rule)


    vertical_ratios_rule = get_vertical_ratio_rule(
        face_measurements,
        quantized_measurements,
    )

    if vertical_ratios_rule is not None:
        rules.append(vertical_ratios_rule)


    lower_face_rule = get_jaw_cheekbone_rule(
        quantized_measurements
    )

    if lower_face_rule is not None:
        rules.append(lower_face_rule)


    jaw_angle_rule = get_jaw_angle_rule(
        quantized_measurements
    )

    if jaw_angle_rule is not None:
        rules.append(jaw_angle_rule)


    chin_angle_rule = get_chin_angle_rule(
        quantized_measurements
    )

    if chin_angle_rule is not None:
        rules.append(chin_angle_rule)

    return rules


def get_face_height_ratio_rule(
    quantized_measurements,
):
    height_level = quantized_measurements[
        "height_to_width_ratio"
    ]

    if height_level >= 1:
        return {
            "source": "face_ratio",
            "face_type": "long",
            "feature": "세로 비율이 상대적으로 큰 긴 얼굴",
            "feature_level": height_level,
            "adjustments": {
                # 여러 영상에서 반복적으로 확인된 핵심 규칙
                "top_volume": -1,
                "side_volume": 1,
                "forehead_exposure": -1,

                # 보조 규칙:
                # 긴 얼굴에서 앞머리 기장을 확보하면
                # 노출되는 세로 길이를 줄일 수 있다는 직접 근거가 있음.
                "bangs_length": 1,
            },
            "effect": (
                "윗머리의 과도한 높이를 줄이고 옆머리 볼륨을 살려 "
                "시선을 가로 방향으로 분산하며, "
                "이마 노출과 얼굴의 세로 강조를 줄임"
            ),
        }

    elif height_level <= -1:
        return {
            "source": "face_ratio",
            "face_type": "short",
            "feature": "가로 비율이 상대적으로 큰 짧은 얼굴",
            "feature_level": height_level,
            "adjustments": {
                # 여러 영상에서 반복적으로 확인된 핵심 규칙
                "top_volume": 1,
                "forehead_exposure": 1,

                # 보조 규칙:
                # 옆머리를 줄여 가로 팽창을 억제한다는 반복 근거가 있음.
                "side_volume": -1,

                # 보조 규칙:
                # 둥근 인상을 줄이기 위해 직선적/샤프한 질감을
                # 사용하는 근거가 일부 영상에서 확인됨.
                "curl_strength": -1,
            },
            "effect": (
                "이마를 드러내고 윗머리 볼륨을 살려 "
                "얼굴의 세로 비율을 늘려 보이게 하고, "
                "옆머리의 가로 팽창을 줄여 전체 비율을 보완"
            ),
        }

    else:
        return {
            "source": "face_ratio",
            "face_type": "average",
            "feature": "세로·가로 비율이 평균적인 얼굴",
            "feature_level": height_level,
            "adjustments": {},
            "effect": (
                "얼굴의 세로·가로 비율이 평균 범위이므로 "
                "종횡비에 대한 특별한 보정은 필요하지 않음"
            ),
        }
    


def get_vertical_ratio_rule(
    face_measurements,
    quantized_measurements,
):
    vertical_ratios = {
        "upper": face_measurements.vertical_ratios.upper,
        "middle": face_measurements.vertical_ratios.middle,
        "lower": face_measurements.vertical_ratios.lower,
    }

    # 현재는 가장 큰 영역 하나를 dominant region으로 선택한다.
    # 향후 upper/middle/lower 각각의 reference percentile을
    # 독립적으로 해석하는 방식도 검토할 수 있음.
    dominant_region = max(
        vertical_ratios,
        key=vertical_ratios.get,
    )

    dominant_level = quantized_measurements[
        f"{dominant_region}_ratio"
    ]

    if dominant_region == "upper":
        return {
            "source": "vertical_ratio",
            "dominant_region": "upper",
            "feature": "상안부 비율이 상대적으로 큰 얼굴",
            "feature_level": dominant_level,
            "adjustments": {
                # 핵심 규칙
                "forehead_exposure": -1,

                # 보조 규칙:
                # 넓은 이마를 덮되 무거운 풀뱅보다는
                # 가벼운 질감이 적합하다는 반복 근거.
                "bangs_weight": -1,

                # 보조 규칙:
                # 5:5 정가르마가 상안부의 세로선을 강조할 수 있어
                # 비대칭 가르마를 활용한다는 근거.
                "parting_asymmetry": 1,
            },
            "effect": (
                "넓은 상안부의 노출 면적을 줄이고 "
                "가벼운 앞머리와 비대칭적인 가르마를 활용해 "
                "이마의 세로 강조를 완화"
            ),
        }

    elif dominant_region == "middle":
        return {
            "source": "vertical_ratio",
            "dominant_region": "middle",
            "feature": "중안부 비율이 상대적으로 큰 얼굴",
            "feature_level": dominant_level,
            "adjustments": {
                # 핵심 규칙
                "bangs_length": 1,
                "side_volume": 1,

                # 보조 규칙:
                # 이마를 완전히 막기보다 일부 노출하여
                # 시선을 위쪽으로 분산한다는 근거.
                "forehead_exposure": 1,

                # 보조 규칙:
                # 컬감을 이용해 중안부의 직선적인 세로 시선을
                # 분산한다는 근거.
                "curl_strength": 1,
            },
            "effect": (
                "앞머리 기장과 옆머리 볼륨을 활용해 "
                "중안부에 집중되는 시선을 머리와 좌우 방향으로 분산"
            ),
        }

    else:
        return {
            "source": "vertical_ratio",
            "dominant_region": "lower",
            "feature": "하안부 비율이 상대적으로 큰 얼굴",
            "feature_level": dominant_level,
            "adjustments": {
                # 현재 직접적인 근거가 가장 명확한 규칙
                "forehead_exposure": 1,
            },
            "effect": (
                "이마를 드러내 시선을 얼굴 위쪽으로 유도하고 "
                "긴 하안부에 집중되는 시선을 분산"
            ),
        }
    

def get_jaw_cheekbone_rule(
    quantized_measurements,
):
    jaw_width_level = quantized_measurements[
        "jaw_to_cheekbone_width_ratio"
    ]

    if jaw_width_level >= 1:
        return {
            "source": "jaw_width",
            "feature": "광대 대비 턱 폭이 넓은 편",
            "feature_level": jaw_width_level,
            "adjustments": {
                # 핵심 규칙
                "forehead_exposure": 1,

                # 보조 규칙:
                # 옆머리/구렛나루 볼륨을 줄여
                # 하안부의 가로 팽창을 억제한다는 근거.
                "side_volume": -1,

                # 보조 규칙:
                # 각진 윤곽을 부드럽게 보이고 싶은 경우
                # 굵은 웨이브를 활용한다는 근거.
                "curl_strength": 1,
            },
            "effect": (
                "이마를 열어 시선을 상단으로 분산하고 "
                "옆머리의 과도한 부피를 줄여 "
                "넓은 하안부가 더 넓어 보이는 것을 방지"
            ),
        }

    elif jaw_width_level <= -1:
        return {
            "source": "jaw_width",
            "feature": "광대 대비 턱 폭이 좁은 편",
            "feature_level": jaw_width_level,
            "adjustments": {
                # 핵심 규칙
                "side_volume": 1,

                # 보조 규칙:
                # 좁아지는 하관과 상부의 대비를 완화하기 위해
                # 관자/측면부의 앞머리 무게감을 활용하는 근거.
                "bangs_weight": 1,

                # 보조 규칙:
                # 곡선 실루엣을 이용해 광대에서 턱으로
                # 급격하게 좁아지는 윤곽을 완화한다는 근거.
                "curl_strength": 1,

                # 보조 규칙:
                # 하트형/마름모형에서 이마를 완전히 열면
                # 윤곽선이 강조될 수 있다는 근거.
                "forehead_exposure": -1,
            },
            "effect": (
                "옆머리 볼륨과 헤어의 곡선감을 이용해 "
                "광대에서 턱으로 급격히 좁아지는 폭의 대비를 완화"
            ),
        }

    else:
        return {
            "source": "jaw_width",
            "feature": "광대 대비 턱 폭이 평균적인 얼굴",
            "feature_level": jaw_width_level,
            "adjustments": {},
            "effect": (
                "광대 대비 턱 폭이 평균 범위이므로 "
                "턱 폭에 대한 특별한 보정은 필요하지 않음"
            ),
        }


def get_jaw_angle_rule(
    quantized_measurements,
):
    jaw_angle_level = quantized_measurements["jaw_angle"]

    # 현재는 좌우 하악각의 평균적인 경향만 사용.
    # TODO: 좌우 차이는 향후 asymmetry 규칙에서 별도 처리.

    if jaw_angle_level >= 1:
        return {
            "source": "jaw_angle",
            "feature": "하악각이 상대적으로 각진 얼굴",
            "feature_level": jaw_angle_level,
            "adjustments": {
                # 여러 영상에서 반복적으로 확인된 핵심 규칙
                "bangs_weight": -1,
                "curl_strength": 1,
            },
            "effect": (
                "무거운 일자 앞머리가 만드는 가로 프레임을 줄이고 "
                "곡선적인 헤어 질감을 활용해 각진 하악선을 부드럽게 완화"
            ),
        }

    elif jaw_angle_level <= -1:
        return {
            "source": "jaw_angle",
            "feature": "하악각이 상대적으로 완만한 얼굴",
            "feature_level": jaw_angle_level,
            "adjustments": {
                # 현재 확보한 영상에서는 완만한 하악각에 대한
                # 독립적인 헤어 보정 규칙의 근거가 부족함.
            },
            "effect": (
                "하악각이 비교적 완만한 편이며 "
                "현재 수집된 근거만으로는 별도의 보정 방향을 적용하지 않음"
            ),
        }

    else:
        return {
            "source": "jaw_angle",
            "feature": "하악각이 평균적인 얼굴",
            "feature_level": jaw_angle_level,
            "adjustments": {},
            "effect": (
                "하악각이 평균 범위이므로 "
                "하악각에 대한 특별한 보정은 필요하지 않음"
            ),
        }
        


def get_chin_angle_rule(
    quantized_measurements,
):
    chin_angle_level = quantized_measurements["chin_angle"]

    if chin_angle_level >= 1:
        return {
            "source": "chin_angle",
            "feature": "턱끝이 상대적으로 뭉툭한 얼굴",
            "feature_level": chin_angle_level,
            "adjustments": {
                # TODO:
                # 뭉툭한 턱끝(blunt_chin)에 대한 헤어 규칙은
                # 둥근 얼굴이나 전체 하안부 형태와 함께 설명되는 경우가 많음.
                # chin_angle 단독 지표에 적용할 수 있는 근거가 더 쌓일 때
                # 별도의 adjustment를 추가할 예정.
            },
            "effect": (
                "턱끝의 선이 비교적 부드럽고 둥글게 나타나는 편이에요. "
                "전체 하안부의 폭과 윤곽을 함께 고려해 헤어 방향을 결정하는 것이 좋아요."
            ),
        }

    elif chin_angle_level <= -1:
        return {
            "source": "chin_angle",
            "feature": "턱끝이 상대적으로 뾰족한 얼굴",
            "feature_level": chin_angle_level,
            "adjustments": {
                # 보조 후보:
                # "curl_strength": 1
                #
                # 일부 영상에서는 떨어지는 컬과 곡선적인 헤어가
                # 뾰족한 턱끝의 날카로운 인상을 부드럽게 만든다고 설명함.
                #
                # 하지만 다른 전문가 자료에서는 턱끝 자체보다
                # 상부 두상과 전체 얼굴 밸런스를 조절하는 것이 중요하다고 설명하여,
                # 현재는 추천 점수에 반영하지 않음.
            },
            "effect": (
                "턱끝이 비교적 가늘고 선명하게 모이는 편이에요. "
                "턱끝만 따로 보기보다 광대와 턱 폭 등 전체 하안부의 형태를 "
                "함께 고려하는 것이 좋아요."
            ),
        }

    else:
        return {
            "source": "chin_angle",
            "feature": "턱끝 각도가 평균적인 얼굴",
            "feature_level": chin_angle_level,
            "adjustments": {},
            "effect": (
                "턱끝의 뾰족함이나 뭉툭함이 한쪽으로 크게 치우치지 않은 "
                "평균적인 형태예요."
            ),
        }


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